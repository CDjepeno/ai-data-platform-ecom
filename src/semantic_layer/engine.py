import trino

from utils.logger import get_logger
from config_env import Config

logger = get_logger(__name__)


def get_trino_connection():

    try:

        conn = trino.dbapi.connect(
            host=Config.TRINO_HOST,
            port=Config.TRINO_PORT,
            user=Config.TRINO_USER,
            catalog=Config.TRINO_CATALOG,
            schema=Config.TRINO_SCHEMA,
        )

        logger.info("✅ Trino connection established")

        return conn

    except Exception as e:

        logger.error(f"❌ Trino connection error: {e}")

        raise