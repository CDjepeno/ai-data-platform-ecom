import logging
from pathlib import Path


from etl_ecom.db.engine import get_duckdb_connection
from etl_ecom.utils.load_sql_files import load_sql_files
from etl_ecom.utils.logger import get_logger



logger = get_logger(__name__)


def init_db():
    engine = get_duckdb_connection()
    
    BASE_DIR = Path(__file__).resolve().parents[1]
    sql_path = BASE_DIR / "sql/metadata/ddl"

        # charger SQL
    queries = load_sql_files(str(sql_path))

    for name, query in queries.items():
        logger.info(f"🚀 Exécution SQL: {name}")
        try:
            engine.execute(query)

            logger.info(f"✅ Exécuté: {name}")

        except Exception as e:
            logger.error(f"❌ Erreur sur {name}: {e}")
            raise
    
    engine.close()
        
if __name__ == "__main__":
    init_db()
