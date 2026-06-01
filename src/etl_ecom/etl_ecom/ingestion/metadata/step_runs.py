from pathlib import Path

from etl_ecom.db.engine import get_duckdb_connection
from etl_ecom.utils.load_sql_files import load_sql_file
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def start_step_run(run_id: str, step_name: str) -> None:
    engine = get_duckdb_connection()
    try:
        BASE_DIR = Path(__file__).resolve().parents[2]
        sql_path = BASE_DIR / "sql/metadata/start_step_run.sql"

        query = load_sql_file(sql_path)
        if not query:
            logger.error(f"❌ Could not load {sql_path}")
            return

        engine.execute(query, [run_id, step_name])
        logger.info(f"✅ Step started: {step_name}")
    except Exception as e:
        logger.error(f"❌ start_step_run error for {step_name}: {e}")
        raise
    finally:
        engine.close()


def finish_step_run(run_id: str, step_name: str, status: str) -> None:
    engine = get_duckdb_connection()
    try:
        BASE_DIR = Path(__file__).resolve().parents[2]
        sql_path = BASE_DIR / "sql/metadata/finish_step_run.sql"

        query = load_sql_file(sql_path)
        if not query:
            logger.error(f"❌ Could not load {sql_path}")
            return

        result = engine.execute(query, [status, run_id, step_name])

        if result.rowcount == 0:
            logger.warning(f"⚠️ No rows updated for step {step_name} (run_id={run_id})")
        else:
            logger.info(f"✅ Step finished: {step_name} ({status})")
    except Exception as e:
        logger.error(f"❌ finish_step_run error for {step_name}: {e}")
        raise
    finally:
        engine.close()
