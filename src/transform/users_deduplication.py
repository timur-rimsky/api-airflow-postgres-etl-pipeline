def deduplicate_users(clean_records):
    latest_by_external_id = {}

    for record in clean_records:
        external_id = record["external_id"]

        if external_id not in latest_by_external_id:
            latest_by_external_id[external_id] = record
            continue

        if record["staging_id"] > latest_by_external_id[external_id]["staging_id"]:
            latest_by_external_id[external_id] = record

    deduplicated_records = list(latest_by_external_id.values())
    rows_deduplicated = len(clean_records) - len(deduplicated_records)

    return {
        "deduplicated_records": deduplicated_records,
        "rows_deduplicated": rows_deduplicated,
    }
