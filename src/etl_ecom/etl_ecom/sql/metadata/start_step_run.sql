INSERT INTO metadata.etl_step_runs
(run_id, step_name, status, started_at)
VALUES (?, ?, 'running', CURRENT_TIMESTAMP)
RETURNING run_id
