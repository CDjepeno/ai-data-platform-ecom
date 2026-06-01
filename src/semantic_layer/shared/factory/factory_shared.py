

from config_env import Config
from shared.cache.redis_service import RedisService


redis_service = RedisService(
    host=Config.VALKEY_HOST,
    port=Config.VALKEY_PORT,
    ttl=Config.VALKEY_TTL,
)