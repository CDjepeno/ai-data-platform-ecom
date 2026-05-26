

from config_env import settings

from shared.cache.redis_service import RedisService


redis_service = RedisService(
    host=settings.valkey_host,
    port=settings.valkey_port,
    ttl=settings.valkey_ttl,
)