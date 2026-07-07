from src.validate.users_validator import validate_user


def test_validate_user_accepts_valid_record():
    normalized_user = {
        "external_id": 1,
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "sincere@example.com",
        "phone": "123-456",
        "website": "example.com",
        "company_name": "Example Company",
    }

    result = validate_user(normalized_user)

    assert result["is_valid"] is True
    assert result["data"]["external_id"] == 1
    assert result["data"]["email"] == "sincere@example.com"
    assert result["errors"] == []


def test_validate_user_rejects_negative_external_id():
    normalized_user = {
        "external_id": -1,
        "name": "Negative Id User",
        "username": "negative_id",
        "email": "negative@example.com",
        "phone": "000-000",
        "website": "negative.example.com",
        "company_name": "Dirty Data LLC",
    }

    result = validate_user(normalized_user)

    assert result["is_valid"] is False
    assert result["data"] is None
    assert result["errors"][0]["field"] == "external_id"


def test_validate_user_rejects_invalid_external_id_type():
    normalized_user = {
        "external_id": "abc",
        "name": "Invalid Id User",
        "username": "invalid_id",
        "email": "invalid-id@example.com",
        "phone": "111-111",
        "website": "invalid-id.example.com",
        "company_name": "Dirty Data LLC",
    }

    result = validate_user(normalized_user)

    assert result["is_valid"] is False
    assert result["data"] is None
    assert result["errors"][0]["field"] == "external_id"


def test_validate_user_rejects_empty_name():
    normalized_user = {
        "external_id": 101,
        "name": "",
        "username": "empty_name",
        "email": "empty-name@example.com",
        "phone": "222-222",
        "website": "empty-name.example.com",
        "company_name": "Dirty Data LLC",
    }

    result = validate_user(normalized_user)

    assert result["is_valid"] is False
    assert result["data"] is None
    assert result["errors"][0]["field"] == "name"


def test_validate_user_rejects_invalid_email():
    normalized_user = {
        "external_id": 102,
        "name": "Invalid Email User",
        "username": "invalid_email",
        "email": "wrong-email",
        "phone": "333-333",
        "website": "invalid-email.example.com",
        "company_name": "Dirty Data LLC",
    }

    result = validate_user(normalized_user)

    assert result["is_valid"] is False
    assert result["data"] is None
    assert result["errors"][0]["field"] == "email"


def test_validate_user_returns_multiple_errors():
    normalized_user = {
        "external_id": "bad-id",
        "name": "",
        "username": "multi_error",
        "email": "not-an-email",
        "phone": "444-444",
        "website": "multi-error.example.com",
        "company_name": "Dirty Data LLC",
    }

    result = validate_user(normalized_user)

    error_fields = {error["field"] for error in result["errors"]}

    assert result["is_valid"] is False
    assert result["data"] is None
    assert "external_id" in error_fields
    assert "name" in error_fields
    assert "email" in error_fields
    assert len(result["errors"]) == 3
