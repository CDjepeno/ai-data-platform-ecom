

from pathlib import Path

from duckdb import DuckDBPyConnection

from etl_ecom.utils.load_sql_files import load_sql_file
from etl_ecom.utils.logger import get_logger
import traceback

logger = get_logger(__name__)


def get_high_watermark_rows(table: str, warehouse_engine: DuckDBPyConnection) -> dict | None:


    try:
        
        BASE_DIR = Path(__file__).resolve().parents[2]

        sql_path = BASE_DIR / "sql/metadata/get_high_watermark.sql"
        
        # 1. Charger la requête SQL
        sql_query = load_sql_file(sql_path)

        if not sql_query:
            logger.error(f"❌ Impossible de charger le fichier SQL watermark.sql")
            return None

        # 2. Log de debug
        logger.debug(f"📄 Requête watermark chargée: {sql_query[:100]}...")

        # 3. Exécuter la requête
        logger.debug(f"🔍 Récupération du watermark pour {table}")
        result = warehouse_engine.execute(sql_query, [table]).fetchone()

        # 4. Vérifier le résultat
        if result is None:
            logger.info(f"📭 Aucun enregistrement dans etl_watermark pour {table}")
            return None

        high_watermark, watermark_id = result

        if high_watermark is None:
            logger.info(f"📭 high_watermark NULL pour {table}")
            return None

        # 5. Convertir et retourner
        watermark_info = {
            "high_watermark": high_watermark,
            "watermark_id": int(watermark_id) if watermark_id is not None else 0
        }

        logger.info(f"✅ Watermark récupéré pour {table}:")
        logger.info(f"   - high_watermark: {watermark_info['high_watermark']}")
        logger.info(f"   - watermark_id: {watermark_info['watermark_id']}")

        return watermark_info

    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération du watermark pour {table}: {e}")
        logger.debug(traceback.format_exc())
        return None