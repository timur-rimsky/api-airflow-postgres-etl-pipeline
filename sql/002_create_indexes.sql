CREATE INDEX IF NOT EXISTS idx_stg_users_raw_run_id
ON stg_users_raw(run_id);

CREATE INDEX IF NOT EXISTS idx_clean_users_run_id
ON clean_users(run_id);

CREATE INDEX IF NOT EXISTS idx_rejected_users_run_id
ON rejected_users(run_id);

CREATE INDEX IF NOT EXISTS idx_clean_users_external_id
ON clean_users(external_id);

CREATE INDEX IF NOT EXISTS idx_etl_load_logs_status
ON etl_load_logs(status);
