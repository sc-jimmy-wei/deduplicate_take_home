import json
from datetime import datetime


def load_json(filename):
    with open(filename) as f:
        return json.load(f)


def parse_date(date_string):
    return datetime.fromisoformat(date_string)


def is_newer(new_item, existing_item):
    return parse_date(new_item["entryDate"]) >= parse_date(existing_item["entryDate"])


def update_map(item_map, key, item, other_map, other_key, change_log):
    if item[key] not in item_map or is_newer(item, item_map[key]):
        if item[key] in item_map:
            log_changes(item_map[item[key]], item, change_log)
            if item_map[item[key]][other_key] in other_map:
                del other_map[item_map[item[key]][other_key]]
        item_map[item[key]] = item
        if item[other_key] not in other_map:
            other_map[item[other_key]] = item


def log_changes(old, new, log):
    changes = {
        key: {"from": old[key], "to": new[key]} for key in old if old[key] != new[key]
    }
    if changes:
        log.append({"source_record": old, "output_record": new, "changes": changes})


def deduplicate():
    data = load_json("leads.json")["leads"]
    id_map, email_map, change_log = {}, {}, []

    for item in data:
        update_map(id_map, "_id", item, email_map, "email", change_log)
        update_map(email_map, "email", item, id_map, "_id", change_log)

    dedup = {"leads": list(id_map.values())}

    print("Deduplicated Result:")
    print(json.dumps(dedup, indent=2))
    print("Change Log:")
    print(json.dumps(change_log, indent=2))


deduplicate()
