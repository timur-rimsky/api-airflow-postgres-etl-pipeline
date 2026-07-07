from src.utils.run_id import generate_run_id
import src.utils.logger as logger
from src.extract.users_api import fetch_users
from src.transform.demo_data import prepare_users_for_pipeline
import src.load.staging_loader as staging_loader
from src.validate.users_validator import prepare_clean_and_rejected_records
import src.load.clean_rejected_loader as cr_loader
from src.transform.users_deduplication import deduplicate_users
from src.load.final_loader import load_final_users


def run_users_pipeline():
    run_id = generate_run_id()
    source = "jsonplaceholder_users"

    failed_step = "start"
    logger.start_run_log(run_id, source)

    try:
        failed_step = "extract_api"
        api_users = fetch_users()

        failed_step = "prepare_demo_data"
        users = prepare_users_for_pipeline(api_users)
        rows_received = len(users)

        failed_step = "staging_load"
        rows_staged = staging_loader.load_raw_users(run_id, source, users)

        failed_step = "staging_read"
        staged_users = staging_loader.get_staged_users(run_id)

        failed_step = "validation"
        prepared = prepare_clean_and_rejected_records(staged_users)

        failed_step = "clean_rejected_load"
        rows_clean = cr_loader.load_clean_records(run_id, prepared["clean_records"])
        rows_rejected = cr_loader.load_rejected_records(
            run_id,
            prepared["rejected_records"],
        )

        failed_step = "deduplication"
        deduplicated = deduplicate_users(prepared["clean_records"])
        rows_deduplicated = deduplicated["rows_deduplicated"]
        final_candidates = deduplicated["deduplicated_records"]
        rows_final_candidates = len(final_candidates)

        failed_step = "final_load"
        final_results = load_final_users(run_id, final_candidates)

        failed_step = "success_log"
        logger.finish_run_log_success(
            run_id,
            rows_received,
            rows_staged,
            rows_clean,
            rows_rejected,
            rows_deduplicated,
            rows_final_candidates,
            final_results["rows_inserted"],
            final_results["rows_updated"],
            final_results["rows_unchanged"],
        )

        return run_id

    except Exception as error:
        logger.finish_run_log_failed(
            run_id,
            failed_step,
            str(error),
        )
        raise


if __name__ == "__main__":
    run_id = run_users_pipeline()
    print(f"Pipeline finished successfully. run_id={run_id}")
