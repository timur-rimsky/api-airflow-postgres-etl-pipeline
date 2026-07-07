from src.validate.users_validator import prepare_clean_and_rejected_records


def test_prepare_clean_and_rejected_records_preserves_raw_record_for_rejected():
    staged_users = [
        {
            "staging_id": 100,
            "raw_record": {
                "id": "bad-id",
                "name": "   ",
                "username": "multi_error",
                "email": "not-an-email",
                "phone": "444-444",
                "website": "multi-error.example.com",
                "company": {"name": "Dirty Data LLC"},
            },
        }
    ]

    result = prepare_clean_and_rejected_records(staged_users)

    assert len(result["clean_records"]) == 0
    assert len(result["rejected_records"]) == 1

    rejected_record = result["rejected_records"][0]

    assert rejected_record["staging_id"] == 100
    assert rejected_record["raw_record"] == staged_users[0]["raw_record"]
    assert isinstance(rejected_record["error_details"], list)


def test_prepare_clean_and_rejected_records_returns_multiple_error_details():
    staged_users = [
        {
            "staging_id": 101,
            "raw_record": {
                "id": "bad-id",
                "name": "   ",
                "username": "multi_error",
                "email": "not-an-email",
                "phone": "444-444",
                "website": "multi-error.example.com",
                "company": {"name": "Dirty Data LLC"},
            },
        }
    ]

    result = prepare_clean_and_rejected_records(staged_users)

    rejected_record = result["rejected_records"][0]
    error_fields = {
        error["field"]
        for error in rejected_record["error_details"]
    }

    assert len(rejected_record["error_details"]) == 3
    assert "external_id" in error_fields
    assert "name" in error_fields
    assert "email" in error_fields
