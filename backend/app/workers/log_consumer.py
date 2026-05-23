import json
import asyncio
from datetime import datetime
import redis.asyncio as aioredis
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.inference_log import InferenceLog
from app.sdk.redact import redact

QUEUE_KEY = "inference_logs"


def _parse_dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


async def process_log(data: dict):
    async with AsyncSessionLocal() as db:
        log = InferenceLog(
            conversation_id=data.get("conversation_id"),
            model=data.get("model"),
            provider=data.get("provider"),
            latency_ms=data.get("latency_ms"),
            prompt_tokens=data.get("prompt_tokens"),
            completion_tokens=data.get("completion_tokens"),
            total_tokens=data.get("total_tokens"),
            status=data.get("status", "success"),
            error_message=data.get("error_message"),
            input_preview=redact(data.get("input_preview") or ""),
            output_preview=redact(data.get("output_preview") or ""),
            request_timestamp=_parse_dt(data.get("request_timestamp")),
            response_timestamp=_parse_dt(data.get("response_timestamp")),
        )
        db.add(log)
        await db.commit()


async def run_consumer():
    client = aioredis.from_url(settings.REDIS_URL)
    print("Log consumer started, waiting for messages...")
    while True:
        try:
            item = await client.blpop(QUEUE_KEY, timeout=5)
            if item:
                _, raw = item
                data = json.loads(raw)
                await process_log(data)
        except Exception as e:
            print(f"Consumer error: {e}")
            await asyncio.sleep(1)
