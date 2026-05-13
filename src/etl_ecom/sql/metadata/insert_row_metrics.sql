-- insert_audit.sql
-- Insert audit log for ingestion runs

INSERT INTO metadata.etl_metrics (
    run_id, 
    table_name, 
    rows_inserted, 
    rows_updated,
    rows_deleted,
    rows_unchanged, 
    records_failed, 
    processed_at 
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);

