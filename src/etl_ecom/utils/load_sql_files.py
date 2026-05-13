from pathlib import Path

from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def load_sql_files(directory: str) -> dict[str, str]:
    path = Path(directory)
    logger.info(f"🔍 Searching SQL in: {path.resolve()}") 

    if not path.exists():
        logger.warning(f"⚠️  SQL folder not found: {directory}")
        return {}

    queries = {}

    for sql_file in sorted(path.glob("**/*.sql")):  # recursive *.sql
        try:
            with open(sql_file, "r", encoding="utf-8") as f:
                query = f.read().strip()

            # Optional: key uses relative path to avoid name collisions
            relative_key = sql_file.relative_to(path).with_suffix('')
            queries[str(relative_key)] = query
            logger.info(f"📄 Loaded: {sql_file.relative_to(path)}")

        except Exception as e:
            logger.error(f"❌ Error loading {sql_file.name}: {e}")

    return queries


def load_sql_file(filepath: Path) -> str:
    """
    Load a SQL file from a given path.

    Args:
        filepath: Full path to the .sql file (e.g. 'src/etl_ecom/ingestion/sql/watermark.sql')

    Returns:
        File contents (string), or empty string if the file is missing
    """
    path = filepath

    if not path.exists():
        logger.warning(f"⚠️  File not found: {path}")
        return ""
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()