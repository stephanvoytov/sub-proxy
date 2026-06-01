import base64
from app.services.merger import merge_subscription
from app.models import ServerEntry


def encode_sub(text: str) -> bytes:
    return base64.b64encode(text.encode())


def test_merge_passthrough_empty_cache():
    original = encode_sub("vless://uuid@host1:443?security=reality#Server1\n")
    result = merge_subscription(original, {}, [])
    decoded = base64.b64decode(result).decode()
    assert "Server1" in decoded


def test_merge_adds_sources():
    original = encode_sub("vless://original-uuid@orig.host:443?security=reality#Original\n")
    sources = {
        "🇷🇺 Russia": [
            ServerEntry(
                raw="vless://ext-uuid@ext.host:8443?type=tcp&security=reality#Extra",
                protocol="vless",
                host="ext.host",
                port=8443,
                name="Extra",
                source_label="🇷🇺 Russia",
            ),
        ],
    }
    result = merge_subscription(original, sources, ["🇷🇺 Russia"])
    decoded = base64.b64decode(result).decode()
    assert "Original" in decoded
    assert "Extra" in decoded
    assert "Russia" in decoded or "🇷🇺" in decoded


def test_merge_dedup_removes_duplicates():
    shared_line = "vless://uuid@shared.host:443?security=reality#Shared"
    original = encode_sub(shared_line + "\n")
    sources = {
        "Source1": [
            ServerEntry(
                raw=shared_line + "#FromSource",
                protocol="vless",
                host="shared.host",
                port=443,
                name="Shared",
                source_label="Source1",
            ),
        ],
    }
    result = merge_subscription(original, sources, ["Source1"], dedup=True)
    decoded = base64.b64decode(result).decode()
    lines = [l for l in decoded.splitlines() if l and not l.startswith("vless://00000000")]
    # Shared server should appear only once
    shared_lines = [l for l in lines if "shared.host" in l]
    assert len(shared_lines) <= 1


def test_merge_no_dedup():
    shared_line = "vless://uuid@shared.host:443?security=reality#Shared"
    original = encode_sub(shared_line + "\n")
    sources = {
        "Source1": [
            ServerEntry(
                raw=shared_line + "#FromSource",
                protocol="vless",
                host="shared.host",
                port=443,
                name="Shared",
                source_label="Source1",
            ),
        ],
    }
    result = merge_subscription(original, sources, ["Source1"], dedup=False)
    decoded = base64.b64decode(result).decode()
    # With dedup off, shared server appears twice
    count = decoded.count("shared.host")
    assert count == 2


def test_merge_preserves_order():
    original = encode_sub("vless://original@orig.com:443?type=tcp#Original\n")
    sources = {
        "Group A": [
            ServerEntry(raw="vless://a@a.com:443?type=tcp#A", name="A", host="a.com", port=443, protocol="vless"),
        ],
        "Group B": [
            ServerEntry(raw="vless://b@b.com:443?type=tcp#B", name="B", host="b.com", port=443, protocol="vless"),
        ],
    }
    result = merge_subscription(original, sources, ["Group A", "Group B"])
    decoded = base64.b64decode(result).decode()
    a_pos = decoded.index("a.com")
    b_pos = decoded.index("b.com")
    assert a_pos < b_pos
