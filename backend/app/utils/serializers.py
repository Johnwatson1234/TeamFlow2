import json
from collections import defaultdict


def parse_json(value: str | None, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def dump_json(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def group_count(rows, key):
    result = defaultdict(int)
    for row in rows:
        result[getattr(row, key)] += 1
    return result
