from datetime import datetime

from airflow.decorators import dag, task
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator

AIRBYTE_CONN_ID = "airbyte_default"
AIRBYTE_CONNECTION_ID = "45efdbc6-79a4-4444-96e1-882f7f440619"


@dag(
    dag_id="postgres_to_iceberg",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["airbyte", "etl", "iceberg"],
)
def postgres_to_iceberg() -> None:

    # Task 1 — Airbyte: PostgreSQL → MinIO (raw Parquet)
    sync = AirbyteTriggerSyncOperator(
        task_id="sync_postgres_to_minio",
        airbyte_conn_id=AIRBYTE_CONN_ID,
        connection_id=AIRBYTE_CONNECTION_ID,
        asynchronous=False,
    )

    @task(task_id="initialize_warehouse")
    def initialize_warehouse() -> None:
        from etl_ecom.configuration.pipeline_factory import PipelineFactory
        PipelineFactory.create_step_service().infra_initializer.initialize()

    @task(task_id="validate_schema")
    def validate_schema() -> None:
        from etl_ecom.configuration.pipeline_factory import PipelineFactory
        PipelineFactory.create_step_service().schema_validator.validate()

    @task(task_id="load_to_iceberg")
    def load_to_iceberg() -> None:
        from etl_ecom.configuration.pipeline_factory import PipelineFactory
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        PipelineFactory.create_step_service().iceberg_loader.load(run_id)

    @task(task_id="build_dbt")
    def build_dbt() -> None:
        from etl_ecom.configuration.pipeline_factory import PipelineFactory
        PipelineFactory.create_step_service().semantic_layer.build_dbt()

    @task(task_id="index_semantic_layer")
    def index_semantic_layer() -> None:
        from etl_ecom.configuration.pipeline_factory import PipelineFactory
        PipelineFactory.create_step_service().semantic_layer.index()

    # Explicit dependency chain — readable, auditable
    (
        sync
        >> initialize_warehouse()
        >> validate_schema()
        >> load_to_iceberg()
        >> build_dbt()
        >> index_semantic_layer()
    )


postgres_to_iceberg()
