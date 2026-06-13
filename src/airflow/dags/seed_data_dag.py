from datetime import datetime
from pathlib import Path

from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import dag, task

_SQL_PATH = Path("/opt/etl_ecom/etl_ecom/scripts/seed/seed_daily_growth.sql")


@dag(
    dag_id="seed_data",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["seed", "data-generation"],
)
def seed_data() -> None:

    @task(task_id="generate_campaign_csv")
    def generate_campaign_csv() -> None:
        from etl_ecom.scripts.seed.generate_campaign_csv import generate
        generate(n=5)

    @task(task_id="seed_daily_growth")
    def seed_daily_growth() -> None:
        import os
        import psycopg2

        sql = _SQL_PATH.read_text()
        conn = psycopg2.connect(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
        finally:
            conn.close()

    trigger_etl_pipeline = TriggerDagRunOperator(
        task_id="trigger_etl_pipeline",
        trigger_dag_id="etl_pipeline",
        wait_for_completion=True,
        poke_interval=30,
    )

    generate_campaign_csv() >> seed_daily_growth() >> trigger_etl_pipeline #type: ignore


seed_data()
