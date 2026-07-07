# API → PostgreSQL ETL Pipeline

Educational Data Engineering project: a Python ETL pipeline that extracts users from a public API, loads raw data into PostgreSQL staging, normalizes and validates records, stores invalid records with error details, deduplicates valid data, and performs an idempotent final load.

## Project Goals

This project demonstrates core Junior Data Engineer / Python ETL Developer skills:

* API extraction
* PostgreSQL schema design
* raw staging layer
* data normalization
* validation with Pydantic
* rejected records flow
* deduplication by business key
* idempotent final load
* ETL audit logging
* Dockerized PostgreSQL
* automated tests with pytest

## Tech Stack

* Python
* PostgreSQL
* Docker / Docker Compose
* psycopg2
* requests
* Pydantic
* pytest

## Data Source

The pipeline extracts users from:

```text
https://jsonplaceholder.typicode.com/users
```

The source API returns 10 user records.

For demonstration purposes, the pipeline intentionally adds:

* controlled dirty records to test validation and rejected flow;
* controlled duplicate records to test deduplication logic.

Expected input size after demo-data injection:

```text
10 API records
+ 5 dirty records
+ 2 duplicate records
= 17 total records
```

## ETL Flow

```text
API
↓
Controlled dirty and duplicate records
↓
stg_users_raw
↓
Normalization
↓
Validation
↓
clean_users / rejected_users
↓
Deduplication
↓
final_users
↓
etl_load_logs
```

## Database Layers

### `etl_load_logs`

Stores one row per pipeline run:

* `run_id`
* `source`
* `status`
* row counters
* failed step
* error message
* start and finish timestamps

Supported statuses:

```text
running
success
failed
partial_success
```

### `stg_users_raw`

Stores all raw input records before validation.

This includes:

* valid API records;
* intentionally injected dirty records;
* intentionally injected duplicate records.

### `clean_users`

Stores normalized and valid records before deduplication.

`external_id` is not unique here because duplicates are allowed at this stage.

### `rejected_users`

Stores invalid records with:

* `staging_id`
* original `raw_record`
* `error_details` as JSON array

Example error details:

```json
[
  {
    "field": "external_id",
    "reason": "Input should be a valid integer"
  },
  {
    "field": "name",
    "reason": "name must not be empty"
  },
  {
    "field": "email",
    "reason": "value is not a valid email address"
  }
]
```

### `final_users`

Stores the final deduplicated user records.

`external_id` is unique in this table.

The final loader supports:

* insert new records;
* update changed records;
* leave unchanged records untouched.

## Deduplication Rule

The source API does not provide an `updated_at` field.

For this educational project, deduplication uses a deterministic fallback rule:

```text
For each external_id, keep the record with the maximum staging_id.
```

This allows the pipeline to demonstrate deduplication while keeping the rule simple and explainable.

## Idempotency

The final load is idempotent.

When the same data is loaded again:

```text
rows_inserted = 0
rows_updated = 0
rows_unchanged = 10
```

This means repeated pipeline runs do not create duplicate rows in `final_users`.

## Project Structure

```text
api-airflow-postgres-etl-pipeline/
│
├── dags/
│   └── users_etl_dag.py
│
├── sql/
│   ├── 001_create_tables.sql
│   └── 002_create_indexes.sql
│
├── src/
│   ├── extract/
│   │   └── users_api.py
│   ├── load/
│   │   ├── clean_rejected_loader.py
│   │   ├── final_loader.py
│   │   └── staging_loader.py
│   ├── normalize/
│   │   └── users_normalizer.py
│   ├── transform/
│   │   ├── demo_data.py
│   │   └── users_deduplication.py
│   ├── utils/
│   │   ├── db.py
│   │   ├── logger.py
│   │   ├── run_id.py
│   │   └── settings.py
│   ├── validate/
│   │   ├── users_model.py
│   │   └── users_validator.py
│   └── pipeline.py
│
├── tests/
│   ├── test_deduplication.py
│   ├── test_idempotency.py
│   ├── test_normalization.py
│   ├── test_rejected.py
│   └── test_validation.py
│
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

## Setup

### 1. Clone repository

```bash
git clone <repository-url>
cd api-airflow-postgres-etl-pipeline
```

### 2. Create `.env`

Copy the example file:

```bash
cp .env.example .env
```

For local Python execution use:

```env
POSTGRES_DB=etl_db
POSTGRES_USER=etl_user
POSTGRES_PASSWORD=etl_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

API_URL=https://jsonplaceholder.typicode.com/users
```

### 3. Start PostgreSQL with Docker Compose

```bash
docker compose up -d
```

PostgreSQL runs inside Docker on port `5432`, mapped to local port `5433`.

```text
localhost:5433 → postgres container:5432
```

### 4. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Create tables

PowerShell:

```powershell
Get-Content sql\001_create_tables.sql | docker exec -i users_etl_postgres psql -U etl_user -d etl_db
```

Bash:

```bash
cat sql/001_create_tables.sql | docker exec -i users_etl_postgres psql -U etl_user -d etl_db
```

### 6. Create indexes

PowerShell:

```powershell
Get-Content sql\002_create_indexes.sql | docker exec -i users_etl_postgres psql -U etl_user -d etl_db
```

Bash:

```bash
cat sql/002_create_indexes.sql | docker exec -i users_etl_postgres psql -U etl_user -d etl_db
```

## Run Pipeline

```bash
python -m src.pipeline
```

Expected output:

```text
Pipeline finished successfully. run_id=<uuid>
```

## Check Latest Run Log

Open PostgreSQL:

```bash
docker exec -it users_etl_postgres psql -U etl_user -d etl_db
```

Run:

```sql
SELECT
    run_id,
    source,
    status,
    rows_received,
    rows_staged,
    rows_clean,
    rows_rejected,
    rows_deduplicated,
    rows_final_candidates,
    rows_inserted,
    rows_updated,
    rows_unchanged,
    failed_step,
    error_message,
    finished_at
FROM etl_load_logs
ORDER BY started_at DESC
LIMIT 1;
```

Expected successful run:

```text
rows_received = 17
rows_staged = 17
rows_clean = 12
rows_rejected = 5
rows_deduplicated = 2
rows_final_candidates = 10
```

If `final_users` already contains the same data, expected final counters are:

```text
rows_inserted = 0
rows_updated = 0
rows_unchanged = 10
```

## Run Tests

```bash
python -m pytest
```

Current test coverage includes:

* normalization tests;
* validation tests;
* rejected records tests;
* deduplication tests;
* final loader idempotency tests.

Some tests require PostgreSQL to be running through Docker Compose.

Expected result:

```text
17 passed
```

## Docker Usage

Docker is used to run PostgreSQL in a reproducible local environment.

The project uses Docker Compose to start:

```text
PostgreSQL 16
```

The Python pipeline itself is currently executed locally, while PostgreSQL runs inside Docker.

For local Python execution:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

If the Python pipeline is later executed inside Docker Compose, the database host should be:

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

## Airflow Status

The project contains a `dags/` directory as preparation for Airflow orchestration.

Current status:

```text
Airflow DAG structure is prepared, but Airflow orchestration is not implemented yet.
```

The current pipeline is orchestrated by:

```text
src/pipeline.py
```

Planned Airflow integration:

```text
Airflow DAG → Python task → run_users_pipeline()
```

This approach keeps ETL business logic inside `src/` and uses Airflow only as an orchestrator.

## Current Limitations

* Airflow DAG is not implemented yet.
* PostgreSQL migrations are executed manually through SQL files.
* Demo dirty and duplicate records are intentionally injected for educational purposes.
* The final loader uses explicit SELECT / INSERT / UPDATE logic instead of compact PostgreSQL `ON CONFLICT`.

## What This Project Demonstrates

This project demonstrates the ability to build a small but realistic ETL pipeline with:

* reliable staging;
* data quality validation;
* rejected records audit;
* deduplication logic;
* idempotent loading;
* PostgreSQL constraints and indexes;
* Dockerized database;
* automated testing;
* run-level logging and failed-run diagnostics.
