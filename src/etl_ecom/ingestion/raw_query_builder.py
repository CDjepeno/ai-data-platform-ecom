
from duckdb import DuckDBPyConnection

from etl_ecom.ingestion.config.table_config import TABLE_CONFIG
from etl_ecom.ingestion.metadata.get_high_watermark import get_high_watermark_rows
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def build_query(table: str, warehouse_engine: DuckDBPyConnection) -> str:
    """
    Construit la requête SQL pour extraire les données d'une table.
    Gère le mode incrémental avec watermark.
    """
    table_config = TABLE_CONFIG.get(table, {})
    
    query = f"SELECT * FROM postgres_db.public.{table}"
    
    incremental_cfg = table_config.get("incremental", {})

    # Mode incrémental : ne récupérer que les nouvelles données
    if incremental_cfg.get("enabled"):
        watermark_column = incremental_cfg.get("watermark_column")
        watermark_id_column = incremental_cfg.get("watermark_id", "id")

        if not watermark_column:
            logger.warning(f"⚠️  Table {table}: incremental activé mais watermark_column manquant")
            return query + ";"

        # Récupérer le dernier watermark connu
        watermark_rows = get_high_watermark_rows(table, warehouse_engine)

        if watermark_rows:
            high_watermark = watermark_rows["high_watermark"]
            watermark_id = watermark_rows["watermark_id"]


            # Construction du filtre avec les bonnes colonnes
            query += f"""
                WHERE
                    {watermark_column} > TIMESTAMP '{high_watermark}'
                    OR (
                        {watermark_column} = TIMESTAMP '{high_watermark}'
                        AND {watermark_id_column} > {watermark_id}
                    )
                ORDER BY {watermark_column}, {watermark_id_column}
                """
        else:
            logger.info(f"  📦 Premier chargement pour {table} (pas de watermark existant)")

    return query