CREATE TABLE IF NOT EXISTS etl_load_logs(
    run_id  UUID PRIMARY KEY,
    source TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('running', 'success', 'failed', 'partial_success')
    ),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    rows_received INTEGER NOT NULL DEFAULT 0 CHECK (rows_received >= 0),
    rows_staged INTEGER NOT NULL DEFAULT 0 CHECK (rows_staged >= 0),
    rows_clean INTEGER NOT NULL DEFAULT 0 CHECK (rows_clean >= 0),
    rows_rejected INTEGER NOT NULL DEFAULT 0 CHECK (rows_rejected >= 0),
    rows_deduplicated INTEGER NOT NULL DEFAULT 0 CHECK (rows_deduplicated >= 0),
    rows_final_candidates INTEGER NOT NULL DEFAULT 0 CHECK (rows_final_candidates >= 0),
    rows_inserted INTEGER NOT NULL DEFAULT 0 CHECK (rows_inserted >= 0),
    rows_updated INTEGER NOT NULL DEFAULT 0 CHECK (rows_updated >= 0),
    rows_unchanged INTEGER NOT NULL DEFAULT 0 CHECK (rows_unchanged >= 0),
    failed_step TEXT,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS stg_users_raw(
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES etl_load_logs(run_id),
    source TEXT NOT NULL,
    raw_record JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clean_users(
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES etl_load_logs(run_id),
    staging_id BIGINT NOT NULL REFERENCES stg_users_raw(id),
    external_id INTEGER NOT NULL CHECK (external_id > 0),
    name TEXT NOT NULL CHECK (BTRIM(name) <> ''),
    username TEXT,
    email TEXT NOT NULL CHECK (BTRIM(email) <> ''),
    phone TEXT,
    website TEXT,
    company_name TEXT,
    cleaned_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rejected_users(
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES etl_load_logs(run_id),
    staging_id BIGINT NOT NULL REFERENCES stg_users_raw(id),
    raw_record JSONB NOT NULL,
    error_details JSONB NOT NULL CHECK (jsonb_typeof(error_details) = 'array'),
    rejected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS final_users(
    id BIGSERIAL PRIMARY KEY,
    external_id INTEGER NOT NULL UNIQUE CHECK (external_id > 0),
    name TEXT NOT NULL CHECK (BTRIM(name) <> ''),
    username TEXT,
    email TEXT NOT NULL CHECK (BTRIM(email) <> ''),
    phone TEXT,
    website TEXT,
    company_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_run_id UUID NOT NULL REFERENCES etl_load_logs(run_id)
);