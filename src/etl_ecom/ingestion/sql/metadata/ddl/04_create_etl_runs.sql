CREATE TABLE IF NOT EXISTS metadata.etl_runs (
    run_id TEXT PRIMARY KEY,        -- Airflow run_id
    pipeline_name TEXT,
    data_source TEXT,
    status TEXT,                   -- SUCCESS / FAILED / RUNNING
    started_at TIMESTAMP,
    finished_at TIMESTAMP
);
