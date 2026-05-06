from pathlib import Path
import traceback
from duckdb import DuckDBPyConnection
import pandas as pd

from etl_ecom.ingestion.config.table_config import TABLE_CONFIG
from etl_ecom.utils.load_sql_files import load_sql_file


def update_high_watermark(
    table: str,
    df: pd.DataFrame,
    warehouse_engine: DuckDBPyConnection
) -> None:

    try:
        print(f"🔥 update watermark appelé pour {table}")
        config = TABLE_CONFIG.get(table)

        if not config:
            return

        incremental_cfg = config.get("incremental", {})

        if not incremental_cfg.get("enabled", False):
            return

        if df.empty:
            return

        column = incremental_cfg.get("watermark_column")
        watermark_id_col = incremental_cfg.get("watermark_id", "id")

        if not column:
            return
        
        if column not in df.columns:
            raise ValueError(
                f"❌ Colonne watermark '{column}' absente du dataframe pour {table}"
            )

        if watermark_id_col not in df.columns:
            raise ValueError(
                f"❌ Colonne watermark_id '{watermark_id_col}' absente du dataframe pour {table}"
            )

        # récupérer la dernière ligne selon (timestamp, id)
        last_row = df.sort_values([column, watermark_id_col]).iloc[-1]

        new_watermark = df[column].max()
        last_id = int(last_row[watermark_id_col])

        # 📄 chemin SQL
        BASE_DIR = Path(__file__).resolve().parents[2]
        sql_path = BASE_DIR / "sql/metadata/upsert_watermark.sql"

        # charger SQL
        sql_query = load_sql_file(sql_path)

        if not sql_query:
            raise ValueError("❌ Impossible de charger upsert_watermark.sql")

        # 🚀 exécution DuckDB
        warehouse_engine.execute(sql_query, [table, new_watermark, last_id])
       
        print(f"✅ Watermark updated for {table}: {new_watermark} (id={last_id})")

    except Exception as e:
        print(f"❌ Erreur update_high_watermark pour {table}")
        print(f"👉 Message: {e}")
        traceback.print_exc()