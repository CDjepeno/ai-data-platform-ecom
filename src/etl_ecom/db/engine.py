from sqlalchemy import create_engine

from etl_ecom.db.db_config import Config

import duckdb

import boto3


def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=Config.MINIO_ENDPOINT,
        aws_access_key_id=Config.MINIO_ROOT_USER,
        aws_secret_access_key=Config.MINIO_ROOT_PASSWORD,
    )

def get_duckdb_connection():
    return duckdb.connect(Config.DUCKDB_PATH)


def get_source_engine():
    return create_engine(Config.SOURCE_URL)