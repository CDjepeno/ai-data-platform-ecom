from datetime import datetime

from airflow.decorators import dag, task
from etl_ecom.factory.pipeline_factory import PipelineFactory


@dag(
    dag_id="etl_pipeline",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "iceberg"],
)
def etl_pipeline():

    @task
    def run_pipeline_task():
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        PipelineFactory.create().execute(run_id)

    run_pipeline_task()


etl_pipeline()
