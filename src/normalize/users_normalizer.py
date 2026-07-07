def safe_strip(value):
    if value is None:
        return None

    return str(value).strip()


def normalize_email(value):
    stripped_value = safe_strip(value)

    if stripped_value is None:
        return None

    return stripped_value.lower()


def normalize_external_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def normalize_company_name(value):
    if not isinstance(value, dict):
        return None

    return safe_strip(value.get("name"))


def normalize_user(raw_user):
    return {
        "external_id":  normalize_external_id(raw_user.get("id")),
        "name":         safe_strip(raw_user.get("name")),
        "username":     safe_strip(raw_user.get("username")),
        "email":        normalize_email(raw_user.get("email")),
        "phone":        safe_strip(raw_user.get("phone")),
        "website":      safe_strip(raw_user.get("website")),
        "company_name": normalize_company_name(raw_user.get("company")),
    }
