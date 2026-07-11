import redis.asyncio as aioredis  # type: ignore

from app.config import settings

# Initialize async Redis client with automatic response decoding
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
