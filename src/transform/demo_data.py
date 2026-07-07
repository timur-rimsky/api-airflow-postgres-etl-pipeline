def get_controlled_dirty_records():
    return [
        {
            "id": -1,
            "name": "Negative Id User",
            "username": "negative_id",
            "email": "negative@example.com",
            "phone": "000-000-0000",
            "website": "negative.example.com",
            "company": {"name": "Dirty Data LLC"},
        },
        {
            "id": "abc",
            "name": "Invalid Id User",
            "username": "invalid_id",
            "email": "invalid-id@example.com",
            "phone": "111-111-1111",
            "website": "invalid-id.example.com",
            "company": {"name": "Dirty Data LLC"},
        },
        {
            "id": 101,
            "name": "   ",
            "username": "empty_name",
            "email": "empty-name@example.com",
            "phone": "222-222-2222",
            "website": "empty-name.example.com",
            "company": {"name": "Dirty Data LLC"},
        },
        {
            "id": 102,
            "name": "Invalid Email User",
            "username": "invalid_email",
            "email": "wrong-email",
            "phone": "333-333-3333",
            "website": "invalid-email.example.com",
            "company": {"name": "Dirty Data LLC"},
        },
        {
            "id": "bad-id",
            "name": "   ",
            "username": "multi_error",
            "email": "not-an-email",
            "phone": "444-444-4444",
            "website": "multi-error.example.com",
            "company": {"name": "Dirty Data LLC"},
        },
    ]


def get_controlled_duplicate_records():
    return [
        {
            "id": 1,
            "name": "Leanne Graham Updated",
            "username": "Bret",
            "email": "leanne.updated@example.com",
            "phone": "999-999-9999",
            "website": "updated-hildegard.org",
            "company": {"name": "Updated Romaguera-Crona"}
        },
        {
            "id": 2,
            "name": "Ervin Howell Updated",
            "username": "Antonette",
            "email": "ervin.updated@example.com",
            "phone": "888-888-8888",
            "website": "updated-anastasia.net",
            "company": {"name": "Updated Deckow-Crist"}
        },
    ]


def prepare_users_for_pipeline(users):
    return (
        users.copy()
        + get_controlled_dirty_records()
        + get_controlled_duplicate_records()
    )
