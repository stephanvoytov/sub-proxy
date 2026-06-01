from urllib.parse import quote


def build_divider(title: str) -> str:
    return (
        "vless://"
        "00000000-0000-0000-0000-000000000000"
        "@divider.local:443"
        f"?encryption=none&type=tcp#{quote(title)}"
    )
