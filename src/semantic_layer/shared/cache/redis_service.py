from __future__ import annotations
from utils.logger import get_logger
import redis.asyncio as redis

logger = get_logger(__name__)


class RedisService:

    def __init__(self, host: str, port: int, ttl: int = 3600):
        self._client = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
        )
        self._default_ttl = ttl

    async def get(self, key: str) -> str | None:
        """Returns cached value or None if not found."""
        try:
            value = await self._client.get(key)
            if value:
                logger.info(f"✅ Cache hit: {key}")
            return value
        except Exception as e:
            logger.warning(f"⚠️ Cache get failed: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Stores value in cache with TTL."""
        try:
            await self._client.setex(
                key,
                ttl or self._default_ttl,
                value,
            )
            logger.info(f"💾 Cache set: {key} (TTL: {ttl or self._default_ttl}s)")
        except Exception as e:
            logger.warning(f"⚠️ Cache set failed: {e}")

    async def exists(self, key: str) -> bool:
        """Checks if key exists in cache."""
        try:
            return bool(await self._client.exists(key))
        except Exception as e:
            logger.warning(f"⚠️ Cache exists failed: {e}")
            return False

    async def close(self) -> None:
        """Closes the connection pool."""
        await self._client.aclose()

    @staticmethod
    def build_intent_key(intent: dict) -> str:
        """
        Builds a deterministic cache key from an intent.
        
        Two intents with same metrics + time range = same key.
        Order of metrics is normalized to avoid cache misses.
        """
        metrics = sorted(intent.get("metrics", []))
        group_by = sorted(intent.get("group_by", []))
        start_time = intent.get("start_time", "")
        end_time = intent.get("end_time", "")
        query_type = intent.get("query_type", "simple")

        if query_type == "comparison":
            p1 = intent.get("period_1", {})
            p2 = intent.get("period_2", {})
            return (
                f"cache:comparison:"
                f"{':'.join(metrics)}:"
                f"{p1.get('start_time')}:{p1.get('end_time')}:"
                f"{p2.get('start_time')}:{p2.get('end_time')}"
            )

        return (
            f"cache:simple:"
            f"{':'.join(metrics)}:"
            f"{':'.join(group_by)}:"
            f"{start_time}:{end_time}"
        )