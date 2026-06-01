import trino

from utils.logger import get_logger
from config_env import settings


logger = get_logger(__name__)


def get_trino_connection():

    try:

        conn = trino.dbapi.connect(
            host=settings.trino_host,
            port=settings.trino_port,
            user=settings.trino_user,
            catalog=settings.trino_catalog,
            schema=settings.trino_schema,
        )

        logger.info("✅ Trino connection established")

        return conn

    except Exception as e:

        logger.error(f"❌ Trino connection error: {e}")

        raise