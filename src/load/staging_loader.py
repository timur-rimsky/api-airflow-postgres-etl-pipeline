from psycopg2.extras import Json
from src.utils.db import get_connection


def load_raw_users(run_id, source, users):
    insert_stg_users_raw_query = """
        INSERT INTO stg_users_raw(run_id, source, raw_record)
        VALUES (%s, %s, %s)
    """

    connection = get_connection()
    cursor = connection.cursor()

    for user in users:
        cursor.execute(
            insert_stg_users_raw_query,
            (run_id, source, Json(user))
        )

    connection.commit()

    cursor.close()
    connection.close()

    return len(users)


def get_staged_users(run_id):
    connection = get_connection()
    cursor = connection.cursor()

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

    cursor.close()
    connection.close()

    staged_users = []

    for row in rows:
        staged_users.append({
            "staging_id": row[0],
            "raw_record": row[1]
        })

    return staged_users
