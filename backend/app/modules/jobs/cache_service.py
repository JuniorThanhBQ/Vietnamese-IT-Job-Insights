import json
from typing import Optional, Any
from loguru import logger
from app.models.redis_client import redis_client


class CacheService:
    """Helper service managing Redis set/get and serialization/deserialization."""

    @staticmethod
    async def get_cache(key: str) -> Optional[Any]:
        """Retrieve and deserialize a JSON cached value by its key."""
        try:
            cached_data = await redis_client.get(key)
            if cached_data:
                logger.info(f"Cache hit for key: {key}")
                return json.loads(cached_data)
            logger.info(f"Cache miss for key: {key}")
            return None
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Failed to read from Redis cache for key {key}: {e}")
            return None

    @staticmethod
    async def set_cache(key: str, value: Any, ttl: int = 43200) -> bool:
        """Serialize a value to JSON and cache it in Redis with a TTL (seconds)."""
        try:
            serialized_data = json.dumps(value, ensure_ascii=False)
            await redis_client.set(key, serialized_data, ex=ttl)
            logger.info(f"Cached value successfully for key: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Failed to write to Redis cache for key {key}: {e}")
            return False
