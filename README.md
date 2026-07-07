# API → PostgreSQL ETL Pipeline

Educational Data Engineering project for a Junior Data Engineer / Python ETL Developer portfolio.

This project implements a Python ETL pipeline that extracts user data from a public API, loads raw JSON into PostgreSQL staging, normalizes and validates records, stores rejected rows with error details, deduplicates valid data, and performs an idempotent final load with audit logging.

## Project Overview

The pipeline demonstrates a small but realistic ETL flow:

```text
External API
   ↓
Controlled dirty and duplicate records
   ↓
PostgreSQL staging
   ↓
Normalization
   ↓
Pydantic validation
   ↓
clean_users / rejected_users
   ↓
Deduplication
   ↓
final_users
   ↓
etl_load_logs
```

The main goal of the project is to show practical Data Engineering skills:

- API extraction
- PostgreSQL staging layer
- data normalization
- data validation with Pydantic
- clean / rejected records flow
- rejected records with error details
- deduplication by business key
- idempotent final loading
- audit logging
- failed-run logging
- transaction-safe database loading
- Dockerized PostgreSQL
- Airflow DAG basics
- unit and integration testing with pytest

## Tech Stack

- Python
- PostgreSQL
- Docker / Docker Compose
- requests
- psycopg2
- Pydantic
- pytest
- Apache Airflow DAG basics

## Data Source

The pipeline extracts users from:

```text
https://jsonplaceholder.typicode.com/users
```

The source API returns 10 user records.

For demonstration purposes, the project intentionally adds:

- 5 controlled dirty records to test validation and rejected flow;
- 2 controlled duplicate records to test deduplication.

Expected input size after demo-data injection:

```text
10 API records
+ 5 dirty records
+ 2 duplicate records
= 17 total records
```

## ETL Flow

### 1. Extract

The pipeline requests user data from the public API.

### 2. Prepare demo data

Controlled dirty and duplicate records are added intentionally.

This makes the project easier to test and explain because the pipeline always receives a predictable mix of:

- valid records;
- invalid records;
- duplicate records.

### 3. Load raw data into staging

All input records are loaded into `stg_users_raw` as raw JSON.

This preserves the original source data before any validation or transformation.

### 4. Normalize records

Nested API fields are flattened and converted into a simpler structure.

For example, company data from the API is normalized into:

```text
company_name
```

### 5. Validate records

Records are validated with Pydantic.

Valid records go to the clean flow.

Invalid records go to the rejected flow with detailed validation errors.

### 6. Load clean and rejected records

Clean and rejected records are loaded in one database transaction.

This means:

```text
clean insert + rejected insert → one commit
any error → one rollback
```

This prevents partial validation results for the same `run_id`.

### 7. Deduplicate clean records

The project deduplicates valid records by business key:

```text
external_id
```

The source API does not provide an `updated_at` field, so the project uses a deterministic educational rule:

```text
For each external_id, keep the record with the maximum staging_id.
```

### 8. Load final users

Final deduplicated records are loaded into `final_users`.

The final load is idempotent:

- new records are inserted;
- changed records are updated;
- unchanged records are left untouched.

### 9. Write audit log

Each pipeline run is logged in `etl_load_logs`.

The log stores:

- run status;
- row counters;
- failed step;
- error message;
- start and finish timestamps.

## Database Schema

### `etl_load_logs`

Stores one row per pipeline run.

Main fields:

- `run_id`
- `source`
- `status`
- `started_at`
- `finished_at`
- `rows_received`
- `rows_staged`
- `rows_clean`
- `rows_rejected`
- `rows_deduplicated`
- `rows_final_candidates`
- `rows_inserted`
- `rows_updated`
- `rows_unchanged`
- `failed_step`
- `error_message`

Supported statuses:

```text
running
success
failed
partial_success
```

### `stg_users_raw`

Stores all raw input records before validation.

This table contains:

- original API records;
- intentionally injected dirty records;
- intentionally injected duplicate records.

### `clean_users`

Stores normalized and valid records before deduplication.

`external_id` is not unique in this table because duplicates are allowed before the deduplication step.

### `rejected_users`

Stores invalid records with validation error details.

Main fields:

- `run_id`
- `staging_id`
- `raw_record`
- `error_details`

Example `error_details`:

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

Stores final deduplicated user records.

`external_id` is unique in this table.

The final loader supports:

- insert new records;
- update changed records;
- skip unchanged records.

## Transaction Handling

Database operations use a shared cursor context manager.

The context manager:

- opens a PostgreSQL connection;
- opens a cursor;
- commits the transaction on success;
- rolls back the transaction on error;
- always closes the cursor and connection.

This reduces duplicated database handling code and makes ETL loading safer.

Clean and rejected records are loaded atomically in one transaction:

```text
load clean records
load rejected records
commit once
```

If either part fails, the full transaction is rolled back.

## Idempotency

The final load is idempotent.

When the same final data is loaded again, the expected result is:

```text
rows_inserted = 0
rows_updated = 0
rows_unchanged = 10
```

This means repeated pipeline runs do not create duplicate rows and do not update unchanged data.

## Airflow Status

The project includes an Airflow DAG:

```text
dags/users_etl_dag.py
```

The DAG calls:

```text
run_users_pipeline()
```

from:

```text
src/pipeline.py
```

Current Airflow status:

```text
Airflow DAG is implemented.
Full Airflow Docker runtime is not included yet.
```

The ETL business logic stays inside `src/`.

Airflow is used only as an orchestration entry point:

```text
Airflow DAG
   ↓
Python task
   ↓
run_users_pipeline()
```

The current `docker-compose.yml` runs PostgreSQL only.

The pipeline is executed locally with:

```bash
python -m src.pipeline
```

### Why Airflow is not included in `requirements.txt`

`apache-airflow` is intentionally not included in the main `requirements.txt` because Airflow is a heavy orchestration platform with its own runtime, scheduler, metadata database, web interface, and dependency constraints.

The current project demonstrates Airflow DAG basics without adding a full Airflow deployment.

Future improvement:

```text
Add full Airflow runtime through Docker Compose.
```

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
│   │
│   ├── load/
│   │   ├── clean_rejected_loader.py
│   │   ├── final_loader.py
│   │   └── staging_loader.py
│   │
│   ├── normalize/
│   │   └── users_normalizer.py
│   │
│   ├── transform/
│   │   ├── demo_data.py
│   │   └── users_deduplication.py
│   │
│   ├── utils/
│   │   ├── db.py
│   │   ├── logger.py
│   │   ├── run_id.py
│   │   └── settings.py
│   │
│   ├── validate/
│   │   ├── users_model.py
│   │   └── users_validator.py
│   │
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
├── pytest.ini
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Clone repository

```bash
git clone <repository-url>
cd api-airflow-postgres-etl-pipeline
```

### 2. Create virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Bash:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Create `.env`

Copy the example file:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Bash:

```bash
cp .env.example .env
```

For local Python execution with PostgreSQL running through Docker Compose, use:

```env
POSTGRES_DB=etl_db
POSTGRES_USER=etl_user
POSTGRES_PASSWORD=your_password_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

API_URL=https://jsonplaceholder.typicode.com/users
```

The Docker container maps PostgreSQL like this:

```text
localhost:5433 → postgres container:5432
```

## Docker Usage

Start PostgreSQL:

```bash
docker compose up -d
```

Check container status:

```bash
docker compose ps
```

Expected service:

```text
users_etl_postgres
```

## Create Tables

PowerShell:

```powershell
Get-Content sql\001_create_tables.sql | docker exec -i users_etl_postgres psql -U etl_user -d etl_db
```

Bash:

```bash
cat sql/001_create_tables.sql | docker exec -i users_etl_postgres psql -U etl_user -d etl_db
```

## Create Indexes

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
    error_message
FROM etl_load_logs
ORDER BY started_at DESC
LIMIT 1;
```

Expected successful run:

```text
status = success
rows_received = 17
rows_staged = 17
rows_clean = 12
rows_rejected = 5
rows_deduplicated = 2
rows_final_candidates = 10
failed_step = null
error_message = null
```

If `final_users` already contains the same final data, expected final counters are:

```text
rows_inserted = 0
rows_updated = 0
rows_unchanged = 10
```

## Run Tests

Run all tests:

```bash
python -m pytest
```

Expected result:

```text
17 passed
```

Run only integration tests:

```bash
python -m pytest -m integration
```

Expected result:

```text
2 passed
```

Run only unit tests:

```bash
python -m pytest -m "not integration"
```

Expected result:

```text
15 passed
```

## Test Structure

Unit tests cover pure Python logic:

- normalization;
- validation;
- rejected records flow;
- deduplication.

Integration tests require PostgreSQL and cover database-dependent behavior:

- final loader idempotency;
- insert / update / unchanged behavior.

The integration tests are marked with:

```python
pytestmark = pytest.mark.integration
```

## Example Final Technical Check

A successful final project check produced:

```text
17 passed
Pipeline finished successfully
```

Latest `etl_load_logs` result:

```text
status = success
rows_received = 17
rows_staged = 17
rows_clean = 12
rows_rejected = 5
rows_deduplicated = 2
rows_final_candidates = 10
rows_inserted = 0
rows_updated = 0
rows_unchanged = 10
```

This confirms that the pipeline is working and the final load is idempotent.

## Current Limitations

- Full Airflow Docker runtime is not included yet.
- PostgreSQL migrations are executed manually through SQL files.
- Demo dirty and duplicate records are intentionally injected for educational purposes.
- The final loader uses explicit `SELECT / INSERT / UPDATE` logic instead of compact PostgreSQL `ON CONFLICT`.
- The project is designed as an educational portfolio project, not as a production deployment.

## Future Improvements

Possible improvements:

- add full Airflow Docker Compose runtime;
- add migration tooling;
- replace explicit final load logic with PostgreSQL `ON CONFLICT`;
- add CI workflow for automated tests;
- add more API sources;
- add more data quality checks;
- add retry logic for API extraction;
- add structured application logging.

## What This Project Demonstrates

This project demonstrates practical Junior Data Engineer skills:

- building an API-to-PostgreSQL ETL pipeline;
- designing staging, clean, rejected and final layers;
- validating data with Pydantic;
- storing rejected records with detailed errors;
- implementing deterministic deduplication;
- building idempotent final loading;
- using PostgreSQL constraints and indexes;
- managing database transactions safely;
- logging successful and failed pipeline runs;
- running PostgreSQL with Docker Compose;
- separating unit and integration tests;
- preparing an Airflow DAG as an orchestration entry point.
