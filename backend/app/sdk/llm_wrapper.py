import time
from datetime import datetime
from app.config import settings
from app.sdk.redact import redact


async def send_log(log: dict):
    try:
        from app.sdk.queue import publish_log
        await publish_log(log)
    except Exception:
        pass


async def call_llm(messages: list, conversation_id: str = None) -> dict:
    provider = settings.LLM_PROVIDER
    model = settings.LLM_MODEL
    request_time = datetime.utcnow().isoformat()
    start = time.time()

    try:
        if provider == "anthropic":
            result = await _call_anthropic(messages, model)
        elif provider == "openai":
            result = await _call_openai(messages, model)
        elif provider == "gemini":
            result = await _call_gemini(messages, model)
        else:
            raise ValueError(f"Unknown provider: {provider}")

        latency = (time.time() - start) * 1000

        import asyncio
        asyncio.create_task(send_log({
            "conversation_id": conversation_id,
            "model": model,
            "provider": provider,
            "latency_ms": round(latency, 2),
            "prompt_tokens": result.get("prompt_tokens"),
            "completion_tokens": result.get("completion_tokens"),
            "total_tokens": result.get("total_tokens"),
            "status": "success",
            "input_preview": redact(messages[-1]["content"][:200]) if messages else "",
            "output_preview": redact(result["content"][:200]),
            "request_timestamp": request_time,
            "response_timestamp": datetime.utcnow().isoformat(),
        }))

        return result

    except Exception as e:
        latency = (time.time() - start) * 1000
        import asyncio
        asyncio.create_task(send_log({
            "conversation_id": conversation_id,
            "model": model,
            "provider": provider,
            "latency_ms": round(latency, 2),
            "status": "error",
            "error_message": str(e),
            "request_timestamp": request_time,
            "response_timestamp": datetime.utcnow().isoformat(),
        }))
        raise


async def _call_anthropic(messages: list, model: str) -> dict:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = await client.messages.create(
        model=model,
        max_tokens=1024,
        messages=messages,
    )
    return {
        "content": response.content[0].text,
        "prompt_tokens": response.usage.input_tokens,
        "completion_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
    }


async def _call_openai(messages: list, model: str) -> dict:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
    )
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
    )
    usage = response.usage
    return {
        "content": response.choices[0].message.content,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
    }

def _to_gemini_messages(messages: list) -> list:
    result = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        result.append({"role": role, "parts": [{"text": msg["content"]}]})
    return result


async def _call_gemini(messages: list, model: str) -> dict:
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(model)
    response = await gemini_model.generate_content_async(_to_gemini_messages(messages))
    meta = response.usage_metadata
    return {
        "content": response.text,
        "prompt_tokens": meta.prompt_token_count,
        "completion_tokens": meta.candidates_token_count,
        "total_tokens": meta.total_token_count,
    }


async def stream_llm(messages: list, conversation_id: str = None):
    provider = settings.LLM_PROVIDER
    model = settings.LLM_MODEL

    if provider == "openai":
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL or None,
        )
        response = await client.chat.completions.create(
            model=model, messages=messages, stream=True,
            stream_options={"include_usage": True},
        )
        async for chunk in response:
            if chunk.usage:
                yield {"__usage__": {
                    "prompt_tokens": chunk.usage.prompt_tokens,
                    "completion_tokens": chunk.usage.completion_tokens,
                    "total_tokens": chunk.usage.total_tokens,
                }}
                continue
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    elif provider == "anthropic":
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        async with client.messages.stream(
            model=model, max_tokens=1024, messages=messages
        ) as stream:
            async for text in stream.text_stream:
                yield text

    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel(model)
        async for chunk in await gemini_model.generate_content_async(
            _to_gemini_messages(messages), stream=True
        ):
            if chunk.text:
                yield chunk.text
