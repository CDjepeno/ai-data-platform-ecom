from sqlalchemy import create_engine

from etl_ecom.db.db_config import Config

import duckdb

import boto3

from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=Config.MINIO_ENDPOINT,
        aws_access_key_id=Config.MINIO_ROOT_USER,
        aws_secret_access_key=Config.MINIO_ROOT_PASSWORD,
    )

def get_duckdb_connection() -> duckdb.DuckDBPyConnection:

    con = duckdb.connect(Config.DBT_DUCKDB_PATH_DEV)

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
            SET s3_endpoint = '{Config.MINIO_ENDPOINT.replace("http://", "")}';
            SET s3_access_key_id = '{Config.MINIO_ROOT_USER}';
            SET s3_secret_access_key = '{Config.MINIO_ROOT_PASSWORD}';
            SET s3_url_style = 'path';
            SET s3_use_ssl = false;
        """)

        logger.info("✅ DuckDB configuré pour MinIO")

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
                    dbname={Config.POSTGRES_DB}
                    user={Config.POSTGRES_USER}
                    password={Config.POSTGRES_PASSWORD}
                    host={Config.POSTGRES_HOST}
                    port={Config.POSTGRES_PORT}
                '
                AS postgres_db
                (TYPE postgres);
            """)

            logger.info("✅ PostgreSQL attaché à DuckDB")
        except Exception as e:
            if "already exists" in str(e):
                logger.info("ℹ️ PostgreSQL déjà attaché")

            else:
                raise

        return con

    except Exception as e:
        logger.error(f"❌ Erreur connexion DuckDB : {e}")
        raise


def get_source_engine():
    return create_engine(Config.SOURCE_URL)

def configure_duckdb_s3(conn: duckdb.DuckDBPyConnection) -> None:
    try:
        conn.execute(f"""
            SET s3_region = 'us-east-1';
            SET s3_endpoint = '{Config.MINIO_ENDPOINT.replace("http://", "")}';
            SET s3_access_key_id = '{Config.MINIO_ROOT_USER}';
            SET s3_secret_access_key = '{Config.MINIO_ROOT_PASSWORD}';
            SET s3_url_style = 'path';
            SET s3_use_ssl = false;
        """)
        logger.info("✅ DuckDB configuré pour MinIO")
    except Exception as e:
        logger.error(f"❌ Erreur configuration MinIO pour DuckDB : {e}")
        raise