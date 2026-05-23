import json
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db, AsyncSessionLocal
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message
from app.schemas import ChatRequest, ConversationOut
from app.sdk.llm_wrapper import call_llm, stream_llm, send_log
from app.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{conversation_id}", response_model=ConversationOut)
async def send_message(
    conversation_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
    )
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.status == ConversationStatus.cancelled:
        raise HTTPException(status_code=400, detail="Conversation is cancelled")

    user_msg = Message(conversation_id=conv.id, role="user", content=request.message)
    db.add(user_msg)
    await db.flush()

    history = [{"role": m.role, "content": m.content} for m in conv.messages[-10:]]
    history.append({"role": "user", "content": request.message})

    llm_result = await call_llm(history, conversation_id=str(conv.id))

    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=llm_result["content"],
        token_count=llm_result.get("total_tokens"),
    )
    db.add(assistant_msg)

    if not conv.title:
        conv.title = request.message[:50]

    await db.commit()

    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conv.id)
    )
    return result.scalar_one()


@router.post("/{conversation_id}/stream")
async def stream_message(
    conversation_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
    )
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.status == ConversationStatus.cancelled:
        raise HTTPException(status_code=400, detail="Conversation is cancelled")

    user_msg = Message(conversation_id=conv.id, role="user", content=request.message)
    db.add(user_msg)
    await db.flush()

    if not conv.title:
        conv.title = request.message[:50]
    await db.commit()

    history = [{"role": m.role, "content": m.content} for m in conv.messages[-10:]]
    history.append({"role": "user", "content": request.message})

    async def event_generator():
        full_response = ""
        usage = {}
        request_time = datetime.utcnow().isoformat()
        start = time.time()
        try:
            async for chunk in stream_llm(history, conversation_id=str(conv.id)):
                if isinstance(chunk, dict) and "__usage__" in chunk:
                    usage = chunk["__usage__"]
                    continue
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as e:
            await send_log({
                "conversation_id": str(conv.id),
                "model": settings.LLM_MODEL,
                "provider": settings.LLM_PROVIDER,
                "latency_ms": round((time.time() - start) * 1000, 2),
                "status": "error",
                "error_message": str(e),
                "request_timestamp": request_time,
                "response_timestamp": datetime.utcnow().isoformat(),
            })
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        latency = round((time.time() - start) * 1000, 2)
        await send_log({
            "conversation_id": str(conv.id),
            "model": settings.LLM_MODEL,
            "provider": settings.LLM_PROVIDER,
            "latency_ms": latency,
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "status": "success",
            "input_preview": history[-1]["content"][:200] if history else "",
            "output_preview": full_response[:200],
            "request_timestamp": request_time,
            "response_timestamp": datetime.utcnow().isoformat(),
        })

        async with AsyncSessionLocal() as new_db:
            assistant_msg = Message(
                conversation_id=conv.id,
                role="assistant",
                content=full_response,
            )
            new_db.add(assistant_msg)
            await new_db.commit()
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
