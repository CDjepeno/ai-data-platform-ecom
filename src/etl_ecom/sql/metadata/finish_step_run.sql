UPDATE metadata.etl_step_runs
SET status = ?,
    finished_at = CURRENT_TIMESTAMP,
    duration = DATEDIFF('second', started_at, CURRENT_TIMESTAMP)
WHERE run_id = ?
  AND step_name = ?