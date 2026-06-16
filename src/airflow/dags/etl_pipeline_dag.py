from datetime import datetime
import os

import requests
from airflow.sdk import dag, task

AIRBYTE_BASE_URL = "http://172.18.0.1:8888/api/public/v1"
AIRBYTE_CONNECTION_ID = "45efdbc6-79a4-4444-96e1-882f7f440619"
AIRBYTE_CLIENT_ID = "734226c8-5388-4ad1-9856-538c72bb517f"
AIRBYTE_CLIENT_SECRET = "Ep5VNnNJbPhTcAi5G5bpVfYJC737Nxg1"

_SERVICE = "airflow.etl_pipeline"


def _get_airbyte_token() -> str:
    """Obtain a short-lived Bearer token from Airbyte."""
    resp = requests.post(
        f"{AIRBYTE_BASE_URL}/applications/token",
        headers={"Content-Type": "application/json"},
        json={
            "grant_type": "client_credentials",
            "client_id": AIRBYTE_CLIENT_ID,
            "client_secret": AIRBYTE_CLIENT_SECRET,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _wait_for_job(job_id: str, token: str, poll_interval: int = 10) -> None:
    """Poll Airbyte until the sync job reaches a terminal state."""
    import time

    while True:
        resp = requests.get(
            f"{AIRBYTE_BASE_URL}/jobs/{job_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        resp.raise_for_status()
        status = resp.json().get("status")

        if status == "succeeded":
            return
        if status in {"failed", "cancelled", "incomplete"}:
            raise RuntimeError(f"Airbyte job {job_id} ended with status: {status}")

        time.sleep(poll_interval)


@dag(
    dag_id="etl_pipeline",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["airbyte", "etl", "iceberg"],
)
def etl_pipeline() -> None:

    @task(task_id="airbyte_sync_postgres_to_minio")
    def airbyte_sync() -> None:
        """Trigger Airbyte sync and wait for completion."""
        from etl_ecom.telemetry import setup_tracing

        tracer = setup_tracing(_SERVICE)
        with tracer.start_as_current_span("airbyte_sync_postgres_to_minio"):
            token = _get_airbyte_token()
            resp = requests.post(
                f"{AIRBYTE_BASE_URL}/jobs",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "connectionId": AIRBYTE_CONNECTION_ID,
                    "jobType": "sync",
                },
                timeout=30,
            )
            resp.raise_for_status()
            job_id = resp.json()["jobId"]
            _wait_for_job(job_id, token)

    @task(task_id="initialize_warehouse")
    def initialize_warehouse() -> None:
        from etl_ecom.factory.pipeline_factory import PipelineFactory
        from etl_ecom.telemetry import setup_tracing

        tracer = setup_tracing(_SERVICE)
        with tracer.start_as_current_span("initialize_warehouse"):
            PipelineFactory.create_step_service().initialize_warehouse()

    @task(task_id="validate_schema")
    def validate_schema() -> None:
        from etl_ecom.factory.pipeline_factory import PipelineFactory
        from etl_ecom.telemetry import setup_tracing

        tracer = setup_tracing(_SERVICE)
        with tracer.start_as_current_span("validate_schema"):
            PipelineFactory.create_step_service().validate_schema()

    @task(task_id="load_to_iceberg")
    def load_to_iceberg() -> None:
        from etl_ecom.factory.pipeline_factory import PipelineFactory
        from etl_ecom.telemetry import setup_tracing

        tracer = setup_tracing(_SERVICE)
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        with tracer.start_as_current_span("load_to_iceberg") as span:
            span.set_attribute("etl.run_id", run_id)
            PipelineFactory.create_step_service().load_to_iceberg(run_id)

    @task(task_id="ingest_csv_campaigns")
    def ingest_csv_campaigns() -> None:
        from etl_ecom.factory.pipeline_factory import PipelineFactory
        from etl_ecom.telemetry import setup_tracing

        tracer = setup_tracing(_SERVICE)
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        with tracer.start_as_current_span("ingest_csv_campaigns") as span:
            span.set_attribute("etl.run_id", run_id)
            PipelineFactory.create_step_service().ingest_csv_campaigns(run_id)

    @task(task_id="build_dbt")
    def build_dbt() -> None:
        from etl_ecom.factory.pipeline_factory import PipelineFactory
        from etl_ecom.telemetry import setup_tracing

        tracer = setup_tracing(_SERVICE)
        with tracer.start_as_current_span("build_dbt"):
            PipelineFactory.create_step_service().build_dbt()

    @task(task_id="index_semantic_layer")
    def index_semantic_layer() -> None:
        from etl_ecom.factory.pipeline_factory import PipelineFactory
        from etl_ecom.telemetry import setup_tracing

        tracer = setup_tracing(_SERVICE)
        with tracer.start_as_current_span("index_semantic_layer"):
            PipelineFactory.create_step_service().index_semantic_layer()

    # Explicit dependency chain
    (
        initialize_warehouse()
        >> airbyte_sync() #type:ignore
        >> ingest_csv_campaigns()
        >> validate_schema()
        >> load_to_iceberg()
        >> build_dbt()
        >> index_semantic_layer()
    )


etl_pipeline()
