import base64
from typing import Dict, List
from urllib.parse import unquote, quote
from app.utils.dividers import build_divider
from app.models import ServerEntry


def merge_subscription(
    original: bytes,
    sources: Dict[str, List[ServerEntry]],
    source_order: List[str],
    dedup: bool = True,
    probed: Dict[str, bool] = None,
) -> bytes:
    if not original:
        return original

    try:
        decoded = base64.b64decode(original + b"==").decode("utf-8")
    except Exception:
        return original

    lines = [x.strip() for x in decoded.splitlines() if x.strip()]

    seen = set()
    final = []

    for line in lines:
        key = line.split("#", 1)[0] if "#" in line else line
        if dedup and key in seen:
            continue
        seen.add(key)
        final.append(line)

    if probed is None:
        probed = {}

    for label in source_order:
        entries = sources.get(label, [])
        if not entries:
            continue

        divider = build_divider(f"⬇️ {label} ⬇️")
        final.append(divider)
        seen.add(divider.split("#", 1)[0] if "#" in divider else divider)

        for entry in entries:
            key = entry.raw.split("#", 1)[0] if "#" in entry.raw else entry.raw
            if dedup and key in seen:
                continue
            seen.add(key)

            if entry.name and entry.raw:
                name = entry.name
                base = entry.raw.rsplit("#", 1)[0]
                encoded_name = quote(
                    name,
                    safe="— []()|*%",
                )
                final.append(f"{base}#{encoded_name}")
            elif entry.raw:
                final.append(entry.raw)

    return base64.b64encode(("\n".join(final) + "\n").encode())
