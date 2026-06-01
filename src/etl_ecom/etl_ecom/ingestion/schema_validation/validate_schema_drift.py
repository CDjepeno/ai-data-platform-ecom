from pathlib import Path

from duckdb import DuckDBPyConnection


from etl_ecom.db.engine import get_duckdb_connection
from etl_ecom.ingestion.schema_validation.mapping import TYPE_MAPPING
from etl_ecom.utils.load_sql_files import load_sql_file
from etl_ecom.utils.logger import get_logger
from etl_ecom.scripts.iceberg.iceberg import get_iceberg_catalog

logger = get_logger(__name__)


def get_iceberg_schema():

    catalog = get_iceberg_catalog()

    rows = []

    for namespace in catalog.list_namespaces():

        for table_identifier in catalog.list_tables(namespace):

            if namespace[0] != "raw":
                continue

            table = catalog.load_table(table_identifier)

            table_name = table_identifier[1]

            for field in table.schema().fields:

                rows.append(
                    {
                        "table_name": table_name,
                        "column_name": field.name,
                        "data_type": str(field.field_type),
                    }
                )

    return rows


def normalize_type(data_type: str) -> str:

    data_type = data_type.lower()

    if data_type.startswith("decimal"):
        return "decimal"

    return TYPE_MAPPING.get(data_type, data_type)


def main(conn: DuckDBPyConnection):

    BASE_DIR = Path(__file__).resolve().parents[2]
    sql_path = BASE_DIR / "sql/schema_validation/get_postgres_schema.sql"

    sql = load_sql_file(sql_path)

    df = conn.execute(sql).fetchdf()

    iceberg_schema = get_iceberg_schema()

    source_columns = set(
        (row["table_name"], row["column_name"], normalize_type(row["data_type"]))
        for _, row in df.iterrows()
    )

    TECHNICAL_COLUMNS = {"ingested_at", "ingestion_date", "run_id"}

    iceberg_columns = set(
        (row["table_name"], row["column_name"], normalize_type(row["data_type"]))
        for row in iceberg_schema
        if row["column_name"] not in TECHNICAL_COLUMNS
    )

    missing_in_iceberg = source_columns - iceberg_columns

    extra_in_iceberg = iceberg_columns - source_columns

    if missing_in_iceberg:
        logger.error("❌ Missing columns in Iceberg:")

    for table_name, column_name, data_type in sorted(missing_in_iceberg):
        logger.error(f"Table={table_name} | Column={column_name} | Type={data_type}")

    if extra_in_iceberg:
        logger.error("❌ Extra columns in Iceberg:")

        for table_name, column_name, data_type in sorted(extra_in_iceberg):
            logger.error(
                f"Table={table_name} | Column={column_name} | Type={data_type}"
            )

    if missing_in_iceberg or extra_in_iceberg:
        raise Exception("❌ Schema drift detected")


if __name__ == "__main__":
    conn = get_duckdb_connection()
    main(conn)
