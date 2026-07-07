from src.utils.db import get_connection


def start_run_log(run_id, source):
    connection = get_connection()
    cursor = connection.cursor()
   
    cursor.execute(
        """
        INSERT INTO etl_load_logs(run_id, source, status)
        VALUES (%s, %s, %s);            
        """,
        (run_id, source, "running")
    )

    connection.commit()

    cursor.close()
    connection.close()


def finish_run_log_success(
    run_id,
    rows_received,
    rows_staged,
    rows_clean,
    rows_rejected,
    rows_deduplicated,
    rows_final_candidates,
    rows_inserted,
    rows_updated,
    rows_unchanged,
):
    connection = get_connection()
    cursor = connection.cursor()
   
    cursor.execute(
        """
        UPDATE etl_load_logs
        SET
            status='success',
            finished_at=NOW(),
            rows_received=%s,
            rows_staged=%s,
            rows_clean=%s,
            rows_rejected=%s,
            rows_deduplicated=%s,
            rows_final_candidates=%s,
            rows_inserted=%s,
            rows_updated=%s,
            rows_unchanged=%s
        WHERE run_id = %s;
        """,
        (
            rows_received,
            rows_staged,
            rows_clean,
            rows_rejected,
            rows_deduplicated,
            rows_final_candidates,
            rows_inserted,
            rows_updated,
            rows_unchanged,
            run_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()


def finish_run_log_failed(run_id, failed_step, error_message):
    connection = get_connection()
    cursor = connection.cursor()
   
    cursor.execute(
        """
        UPDATE etl_load_logs
        SET
            status='failed',
            finished_at=NOW(),
            failed_step=%s,
            error_message=%s            
        WHERE run_id = %s;
        """,
        (failed_step, error_message, run_id)
    )

    connection.commit()

    cursor.close()
    connection.close()



