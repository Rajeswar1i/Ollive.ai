from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.inference_log import InferenceLog
from app.schemas import IngestLogRequest
from datetime import datetime

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/logs")
async def ingest_log(payload: IngestLogRequest, db: AsyncSession = Depends(get_db)):
    log = InferenceLog(
        conversation_id=payload.conversation_id,
        model=payload.model,
        provider=payload.provider,
        latency_ms=payload.latency_ms,
        prompt_tokens=payload.prompt_tokens,
        completion_tokens=payload.completion_tokens,
        total_tokens=payload.total_tokens,
        status=payload.status,
        error_message=payload.error_message,
        input_preview=payload.input_preview,
        output_preview=payload.output_preview,
        request_timestamp=datetime.fromisoformat(payload.request_timestamp) if payload.request_timestamp else None,
        response_timestamp=datetime.fromisoformat(payload.response_timestamp) if payload.response_timestamp else None,
    )
    db.add(log)
    await db.commit()
    return {"status": "ok"}
