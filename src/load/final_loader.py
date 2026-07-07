from src.utils.db import get_connection


def load_final_users(run_id, final_candidates):
    select_query = """
    SELECT name, username, email, phone, website, company_name
    FROM final_users
    WHERE external_id = %s;
    """

    insert_query = """
    INSERT INTO final_users (
        external_id,
        name,
        username,
        email,
        phone,
        website,
        company_name,
        last_seen_run_id
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """

    update_query = """
    UPDATE final_users
    SET
        name = %s,
        username = %s,
        email = %s,
        phone = %s,
        website = %s,
        company_name = %s,
        updated_at = NOW(),
        last_seen_run_id = %s
    WHERE external_id = %s;
    """

    rows_inserted = 0
    rows_updated = 0
    rows_unchanged = 0

    connection = get_connection()
    cursor = connection.cursor()

    for candidate in final_candidates:
        cursor.execute(select_query, (candidate["external_id"],))

        existing = cursor.fetchone()

        if existing is None:
            rows_inserted += 1

            cursor.execute(
                insert_query, (
                    candidate["external_id"],
                    candidate["name"],
                    candidate["username"],
                    candidate["email"],
                    candidate["phone"],
                    candidate["website"],
                    candidate["company_name"],
                    run_id,
                )
            )
        else:
            new_values = (
                candidate["name"],
                candidate["username"],
                candidate["email"],
                candidate["phone"],
                candidate["website"],
                candidate["company_name"],
            )

            if existing != new_values:
                rows_updated += 1

                cursor.execute(
                    update_query,
                    (
                        candidate["name"],
                        candidate["username"],
                        candidate["email"],
                        candidate["phone"],
                        candidate["website"],
                        candidate["company_name"],
                        run_id,
                        candidate["external_id"],
                    )
                )
            else:
                rows_unchanged += 1

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "rows_inserted": rows_inserted,
        "rows_updated": rows_updated,
        "rows_unchanged": rows_unchanged,
    }
