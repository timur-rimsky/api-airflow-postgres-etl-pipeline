from src.transform.users_deduplication import deduplicate_users


def test_deduplicate_users_keeps_record_with_max_staging_id():
    clean_records = [
        {
            "staging_id": 10,
            "external_id": 1,
            "name": "Old Name",
            "username": "old_user",
            "email": "old@example.com",
            "phone": "111",
            "website": "old.example.com",
            "company_name": "Old Company",
        },
        {
            "staging_id": 20,
            "external_id": 1,
            "name": "New Name",
            "username": "new_user",
            "email": "new@example.com",
            "phone": "222",
            "website": "new.example.com",
            "company_name": "New Company",
        },
    ]

    result = deduplicate_users(clean_records)

    assert len(result["deduplicated_records"]) == 1
    assert result["rows_deduplicated"] == 1
    assert result["deduplicated_records"][0]["staging_id"] == 20
    assert result["deduplicated_records"][0]["name"] == "New Name"


def test_deduplicate_users_keeps_all_records_when_no_duplicates():
    clean_records = [
        {
            "staging_id": 10,
            "external_id": 1,
            "name": "User One",
            "username": "user_one",
            "email": "one@example.com",
            "phone": "111",
            "website": "one.example.com",
            "company_name": "Company One",
        },
        {
            "staging_id": 20,
            "external_id": 2,
            "name": "User Two",
            "username": "user_two",
            "email": "two@example.com",
            "phone": "222",
            "website": "two.example.com",
            "company_name": "Company Two",
        },
    ]

    result = deduplicate_users(clean_records)

    assert len(result["deduplicated_records"]) == 2
    assert result["rows_deduplicated"] == 0


def test_deduplicate_users_handles_mixed_records():
    clean_records = [
        {
            "staging_id": 10,
            "external_id": 1,
            "name": "Old User One",
            "username": "old_one",
            "email": "old-one@example.com",
            "phone": "111",
            "website": "old-one.example.com",
            "company_name": "Old Company",
        },
        {
            "staging_id": 20,
            "external_id": 2,
            "name": "User Two",
            "username": "user_two",
            "email": "two@example.com",
            "phone": "222",
            "website": "two.example.com",
            "company_name": "Company Two",
        },
        {
            "staging_id": 30,
            "external_id": 1,
            "name": "New User One",
            "username": "new_one",
            "email": "new-one@example.com",
            "phone": "333",
            "website": "new-one.example.com",
            "company_name": "New Company",
        },
        {
            "staging_id": 40,
            "external_id": 3,
            "name": "User Three",
            "username": "user_three",
            "email": "three@example.com",
            "phone": "444",
            "website": "three.example.com",
            "company_name": "Company Three",
        },
    ]

    result = deduplicate_users(clean_records)

    deduplicated_records = result["deduplicated_records"]
    external_ids = {record["external_id"] for record in deduplicated_records}

    user_one = [
        record
        for record in deduplicated_records
        if record["external_id"] == 1
    ][0]

    assert len(deduplicated_records) == 3
    assert result["rows_deduplicated"] == 1
    assert external_ids == {1, 2, 3}
    assert user_one["staging_id"] == 30
    assert user_one["name"] == "New User One"
