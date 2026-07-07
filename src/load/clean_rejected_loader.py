from psycopg2.extras import Json

from src.utils.db import get_db_cursor


def load_clean_records(run_id, clean_records):
    with get_db_cursor() as (_, cursor):
        for record in clean_records:
            cursor.execute(
                """
                INSERT INTO clean_users (
                    run_id,
                    staging_id,
                    external_id,
                    name,
                    username,
                    email,
                    phone,
                    website,
                    company_name
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    run_id,
                    record["staging_id"],
                    record["external_id"],
                    record["name"],
                    record["username"],
                    record["email"],
                    record["phone"],
                    record["website"],
                    record["company_name"],
                )
            )

    return len(clean_records)


def load_rejected_records(run_id, rejected_records):
    with get_db_cursor() as (_, cursor):
        for record in rejected_records:
            cursor.execute(
                """
                INSERT INTO rejected_users (
                    run_id,
                    staging_id,
                    raw_record,
                    error_details
                )
                VALUES (%s, %s, %s, %s);
                """,
                (
                    run_id,
                    record["staging_id"],
                    Json(record["raw_record"]),
                    Json(record["error_details"]),
                )
            )

    return len(rejected_records)
