FROM apache/airflow:3.2.2-python3.12

USER root
RUN mkdir -p /app/warehouse && chown -R 50000 /app

USER airflow

# Copy the full etl_ecom project (pyproject.toml + package)
COPY --chown=airflow:airflow src/etl_ecom /opt/etl_ecom

RUN pip install --no-cache-dir \
    "numpy<2"  \ 
    "apache-airflow-providers-airbyte>=4.0.0" \
    "duckdb>=1.5.2" \
    "pyarrow>=14.0.0,<15.0.0" \
    "pyiceberg>=0.7.0" \
    "boto3==1.40.18" \
    "s3fs==2023.12.2" \
    "pydantic>=2.11.7" \
    "pydantic-settings>=2.10.1" \
    "python-dotenv>=1.2.2" \
    "httpx>=0.28.1,<0.29.0" \
    "trino>=0.337.0,<0.338.0" \
    "psycopg2-binary>=2.9.12" \
    "pyyaml>=6.0.3"