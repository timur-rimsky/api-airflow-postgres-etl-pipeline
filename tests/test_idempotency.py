from src.load.final_loader import load_final_users
from src.utils.db import get_connection
from src.utils.logger import start_run_log
from src.utils.run_id import generate_run_id


TEST_SOURCE = "pytest_final_loader"
TEST_EXTERNAL_ID = 999001


def cleanup_test_data():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM final_users
        WHERE external_id = %s;
        """,
        (TEST_EXTERNAL_ID,),
    )

    cursor.execute(
        """
        DELETE FROM etl_load_logs
        WHERE source = %s;
        """,
        (TEST_SOURCE,),
    )

    connection.commit()

    cursor.close()
    connection.close()


def test_load_final_users_is_idempotent_for_same_record():
    cleanup_test_data()

    run_id = generate_run_id()
    start_run_log(run_id, TEST_SOURCE)

    final_candidates = [
        {
            "external_id": TEST_EXTERNAL_ID,
            "name": "Test User",
            "username": "test_user",
            "email": "test@example.com",
            "phone": "123-456",
            "website": "test.example.com",
            "company_name": "Test Company",
        }
    ]

    try:
        first_result = load_final_users(run_id, final_candidates)
        second_result = load_final_users(run_id, final_candidates)

        assert first_result["rows_inserted"] == 1
        assert first_result["rows_updated"] == 0
        assert first_result["rows_unchanged"] == 0

        assert second_result["rows_inserted"] == 0
        assert second_result["rows_updated"] == 0
        assert second_result["rows_unchanged"] == 1

    finally:
        cleanup_test_data()


def test_load_final_users_updates_changed_record():
    cleanup_test_data()

    run_id = generate_run_id()
    start_run_log(run_id, TEST_SOURCE)

    original_candidates = [
        {
            "external_id": TEST_EXTERNAL_ID,
            "name": "Original User",
            "username": "test_user",
            "email": "original@example.com",
            "phone": "123-456",
            "website": "test.example.com",
            "company_name": "Original Company",
        }
    ]

    updated_candidates = [
        {
            "external_id": TEST_EXTERNAL_ID,
            "name": "Updated User",
            "username": "test_user",
            "email": "updated@example.com",
            "phone": "123-456",
            "website": "test.example.com",
            "company_name": "Updated Company",
        }
    ]

    try:
        first_result = load_final_users(run_id, original_candidates)
        second_result = load_final_users(run_id, updated_candidates)

        assert first_result["rows_inserted"] == 1
        assert first_result["rows_updated"] == 0
        assert first_result["rows_unchanged"] == 0

        assert second_result["rows_inserted"] == 0
        assert second_result["rows_updated"] == 1
        assert second_result["rows_unchanged"] == 0

    finally:
        cleanup_test_data()
