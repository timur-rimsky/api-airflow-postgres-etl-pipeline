from psycopg2.extras import Json

from src.utils.db import get_db_cursor


def _insert_clean_records(cursor, run_id, clean_records):
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


def _insert_rejected_records(cursor, run_id, rejected_records):
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


def load_clean_and_rejected_records(run_id, clean_records, rejected_records):
    with get_db_cursor() as (_, cursor):
        rows_clean = _insert_clean_records(cursor, run_id, clean_records)
        rows_rejected = _insert_rejected_records(cursor, run_id, rejected_records)

    return {
        "rows_clean": rows_clean,
        "rows_rejected": rows_rejected,
    }
