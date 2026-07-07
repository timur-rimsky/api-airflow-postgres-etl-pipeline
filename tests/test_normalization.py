from src.normalize.users_normalizer import normalize_user


def test_normalize_user_basic_fields():
    raw_user = {
        "id": "101",
        "name": "  Ivan Petrov  ",
        "username": "  ivan_p  ",
        "email": "  USER@EXAMPLE.COM  ",
        "phone": "  123-456  ",
        "website": "  example.com  ",
        "company": {"name": "  Example Company  "},
    }

    result = normalize_user(raw_user)

    assert result["external_id"] == 101
    assert result["name"] == "Ivan Petrov"
    assert result["username"] == "ivan_p"
    assert result["email"] == "user@example.com"
    assert result["phone"] == "123-456"
    assert result["website"] == "example.com"
    assert result["company_name"] == "Example Company"


def test_normalize_user_keeps_invalid_external_id_for_validation():
    raw_user = {
        "id": "abc",
        "name": "Invalid Id User",
        "username": "invalid_id",
        "email": "invalid-id@example.com",
        "phone": "111-111-1111",
        "website": "invalid-id.example.com",
        "company": {"name": "Dirty Data LLC"},
    }

    result = normalize_user(raw_user)

    assert result["external_id"] == "abc"
    assert result["name"] == "Invalid Id User"
    assert result["email"] == "invalid-id@example.com"


def test_normalize_user_handles_none_values():
    raw_user = {
        "id": None,
        "name": None,
        "username": None,
        "email": None,
        "phone": None,
        "website": None,
        "company": None,
    }

    result = normalize_user(raw_user)

    assert result["external_id"] is None
    assert result["name"] is None
    assert result["username"] is None
    assert result["email"] is None
    assert result["phone"] is None
    assert result["website"] is None
    assert result["company_name"] is None


def test_normalize_user_handles_invalid_company_structure():
    raw_user = {
        "id": 10,
        "name": "Company Broken",
        "username": "company_broken",
        "email": "company@example.com",
        "phone": "555-555",
        "website": "company.example.com",
        "company": "not-a-dict",
    }

    result = normalize_user(raw_user)

    assert result["external_id"] == 10
    assert result["company_name"] is None
