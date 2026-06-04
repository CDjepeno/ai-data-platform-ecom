from sqlalchemy import create_engine


import duckdb

import boto3

from etl_ecom.utils.logger import get_logger
from etl_ecom.db.db_config import settings

logger = get_logger(__name__)


def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_root_user,
        aws_secret_access_key=settings.minio_root_password,
    )


def get_duckdb_connection() -> duckdb.DuckDBPyConnection:

    con = duckdb.connect(settings.dbt_duckdb_path_dev)

    try:

        # =========================
        # HTTPFS / MINIO
        # =========================

        con.execute("""
            INSTALL httpfs;
            LOAD httpfs;
        """)

        con.execute(f"""
            SET s3_region = 'us-east-1';
            SET s3_endpoint = '{settings.minio_endpoint.replace("http://", "")}';
            SET s3_access_key_id = '{settings.minio_root_user}';
            SET s3_secret_access_key = '{settings.minio_root_password}';
            SET s3_url_style = 'path';
            SET s3_use_ssl = false;
        """)

        # =========================
        # POSTGRES
        # =========================
        try:

            con.execute("""
                INSTALL postgres;
                LOAD postgres;
            """)

            con.execute(f"""
                ATTACH '
                    dbname={settings.postgres_db}
                    user={settings.postgres_user}
                    password={settings.postgres_password}
                    host={settings.postgres_host}
                    port={settings.postgres_port}
                    sslmode=verify-ca
                    sslrootcert=/app/certs/ovh-postgres.pem
                '
                AS postgres_db
                (TYPE postgres);
            """)

            logger.info("✅ PostgreSQL attached to DuckDB")
        except Exception as e:
            if "already exists" in str(e):
                logger.info("ℹ️ PostgreSQL already attached")

            else:
                raise

        return con

    except Exception as e:
        logger.error(f"❌ DuckDB connection error: {e}")
        raise


def get_source_engine():
    return create_engine(settings.source_url)


def configure_duckdb_s3(conn: duckdb.DuckDBPyConnection) -> None:
    try:
        conn.execute(f"""
            SET s3_region = 'us-east-1';
            SET s3_endpoint = '{settings.minio_endpoint.replace("http://", "")}';
            SET s3_access_key_id = '{settings.minio_root_user}';
            SET s3_secret_access_key = '{settings.minio_root_password}';
            SET s3_url_style = 'path';
            SET s3_use_ssl = false;
        """)
    except Exception as e:
        logger.error(f"❌ MinIO configuration error for DuckDB: {e}")
        raise



