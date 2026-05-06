CREATE TABLE IF NOT EXISTS metadata.etl_step_runs (
    id BIGINT,
    run_id TEXT,
    step_name TEXT,               -- extract_users / load_orders / dbt_model_x
    status TEXT,
    duration DOUBLE,
    started_at TIMESTAMP,
    finished_at TIMESTAMP
);
