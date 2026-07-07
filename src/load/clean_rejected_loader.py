from psycopg2.extras import Json

from src.utils.db import get_connection


def load_clean_records(run_id, clean_records):
    insert_clean_user_query = """
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
    """

    connection = get_connection()
    cursor = connection.cursor()

    for record in clean_records:
        cursor.execute(
            insert_clean_user_query,
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
            ),
        )

    connection.commit()

    cursor.close()
    connection.close()

    return len(clean_records)


def load_rejected_records(run_id, rejected_records):
    insert_rejected_user_query = """
    INSERT INTO rejected_users (
        run_id,
        staging_id,
        raw_record,
        error_details
    )
    VALUES (%s, %s, %s, %s);
    """

    connection = get_connection()
    cursor = connection.cursor()

    for record in rejected_records:
        cursor.execute(
            insert_rejected_user_query,
            (
                run_id,
                record["staging_id"],
                Json(record["raw_record"]),
                Json(record["error_details"]),
            ),
        )

    connection.commit()

    cursor.close()
    connection.close()

    return len(rejected_records)
