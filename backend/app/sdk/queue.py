import json
import redis.asyncio as aioredis
from app.config import settings

QUEUE_KEY = "inference_logs"

async def publish_log(log: dict):
    client = aioredis.from_url(settings.REDIS_URL)
    try:
        await client.rpush(QUEUE_KEY, json.dumps(log))
    finally:
        await client.aclose()
