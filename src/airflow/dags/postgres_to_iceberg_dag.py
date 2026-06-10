from datetime import datetime

from airflow.decorators import dag, task
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from etl_ecom.configuration.pipeline_factory import PipelineFactory

AIRBYTE_CONN_ID = "airbyte_default"
AIRBYTE_CONNECTION_ID = "45efdbc6-79a4-4444-96e1-882f7f440619"


@dag(
    dag_id="postgres_to_iceberg",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["airbyte", "etl", "iceberg"],
)
def postgres_to_iceberg():
    sync = AirbyteTriggerSyncOperator(
        task_id="airbyte_postgres_to_minio",
        airbyte_conn_id=AIRBYTE_CONN_ID,
        connection_id=AIRBYTE_CONNECTION_ID,
        asynchronous=False,
    )

    @task
    def run_iceberg_transform():
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        PipelineFactory.create().execute(run_id)

    sync >> run_iceberg_transform()


postgres_to_iceberg()
