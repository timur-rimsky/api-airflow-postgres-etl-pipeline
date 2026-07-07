from pydantic import ValidationError
from src.validate.users_model import UserModel
from src.normalize.users_normalizer import normalize_user


def validate_user(normalized_user):
    try:
        user = UserModel(**normalized_user)

        return {
            "is_valid": True,
            "data": user.model_dump(),
            "errors": []
        }
    except ValidationError as error:
        error_details = []

        for validation_error in error.errors():
            error_details.append({
                "field": validation_error["loc"][0],
                "reason": validation_error["msg"]
            })

        return {
            "is_valid": False,
            "data": None,
            "errors": error_details
        }


def validate_users(normalized_users):
    valid_records = []
    rejected_records = []

    for user in normalized_users:
        result = validate_user(user)

        if result["is_valid"]:
            valid_records.append(result["data"])
        else:
            rejected_records.append({
                "record": user,
                "errors": result["errors"]
            })

    return {
        "valid_records": valid_records,
        "rejected_records": rejected_records
    }


def prepare_clean_and_rejected_records(staged_users):
    clean_records = []
    rejected_records = []

    for user in staged_users:
        raw_record = user["raw_record"]
        staging_id = user["staging_id"]

        normalized_user = normalize_user(raw_record)

        result = validate_user(normalized_user)

        if result["is_valid"]:
            clean_records.append({
                "staging_id": staging_id,
                **result["data"],
            })
        else:
            rejected_records.append({
                "staging_id": staging_id,
                "raw_record": raw_record,
                "error_details": result["errors"],
            })

    return {
        "clean_records": clean_records,
        "rejected_records": rejected_records,
    }
