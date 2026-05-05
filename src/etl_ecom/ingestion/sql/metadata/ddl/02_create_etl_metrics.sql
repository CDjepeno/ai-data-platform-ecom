CREATE TABLE IF NOT EXISTS metadata.etl_metrics (
    id BIGINT,
    run_id TEXT,
    table_name TEXT,
    rows_inserted INTEGER,
    rows_updated INTEGER,
    rows_deleted INTEGER,
    rows_unchanged INTEGER,
    records_failed INTEGER,
    processed_at TIMESTAMP
)
