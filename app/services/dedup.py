from typing import List
from collections import defaultdict
from app.models import ServerEntry


def server_key(entry: ServerEntry) -> str:
    return entry.raw.split("#", 1)[0] if "#" in entry.raw else entry.raw


def deduplicate(entries: List[ServerEntry]) -> List[ServerEntry]:
    seen = {}
    result = []

    for entry in entries:
        key = server_key(entry)
        if key not in seen:
            seen[key] = entry
            result.append(entry)

    return result
