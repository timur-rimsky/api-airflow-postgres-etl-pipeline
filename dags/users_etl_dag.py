from datetime import datetime

from airflow.sdk import dag, task

from src.pipeline import run_users_pipeline


@dag(
    dag_id="users_api_postgres_etl",
    description="API to PostgreSQL ETL pipeline with validation, rejected records, deduplication and audit logs",
    schedule="@daily",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["etl", "postgres", "api", "data-quality"],
)
def users_api_postgres_etl():
    @task()
    def run_pipeline():
        run_id = run_users_pipeline()
        print(f"Pipeline finished successfully. run_id={run_id}")

        return run_id

    run_pipeline()


users_api_postgres_etl()
