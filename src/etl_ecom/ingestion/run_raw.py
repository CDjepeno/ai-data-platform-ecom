from etl_ecom.ingestion.config.table_config import TABLE_CONFIG
from etl_ecom.ingestion.metadata.step_runs import finish_step_run, start_step_run
from etl_ecom.ingestion.run_raw_table_to_minio import ingest_raw_table_to_minio


def ingest_raw_to_minio(run_id: str):
    

    for table in TABLE_CONFIG.keys():
        step_name = f"extract_{table}"

        start_step_run(run_id, step_name)
        try:
            ingest_raw_table_to_minio(table, run_id)
            finish_step_run(run_id, step_name, "success")
        except Exception:
            finish_step_run(run_id, step_name, "failed")
            raise