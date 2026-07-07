from psycopg2.extras import Json
from src.utils.db import get_db_cursor


def load_raw_users(run_id, source, users):
    with get_db_cursor() as (_, cursor):
        for user in users:
            cursor.execute(
                """
                INSERT INTO stg_users_raw(run_id, source, raw_record)
                VALUES (%s, %s, %s)
                """,
                (run_id, source, Json(user))
            )

    return len(users)


def get_staged_users(run_id):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT id, raw_record
            FROM stg_users_raw
            WHERE run_id = %s
            ORDER BY id;
            """,
            (run_id,)
        )

        rows = cursor.fetchall()

    staged_users = []

    for row in rows:
        staged_users.append({
            "staging_id": row[0],
            "raw_record": row[1]
        })

    return staged_users
