from app.services.dedup import deduplicate
from app.models import ServerEntry


def test_dedup_removes_duplicates():
    raw = "vless://ae5ba4be-7262-4199-bd62-210ed8999b9f@2.59.43.249:5443?type=tcp&security=reality&flow=xtls-rprx-vision&fp=chrome&pbk=key&sni=test.ru#Finland"
    raw_diff = "vless://ae5ba4be-7262-4199-bd62-210ed8999b9f@2.59.43.250:5443?type=tcp&security=reality&flow=xtls-rprx-vision&fp=chrome&pbk=key&sni=test.ru#Finland"
    entries = [
        ServerEntry(raw=raw, protocol="vless", host="2.59.43.249", port=5443),
        ServerEntry(raw=raw, protocol="vless", host="2.59.43.249", port=5443),
        ServerEntry(raw=raw_diff, protocol="vless", host="2.59.43.250", port=5443),
    ]
    result = deduplicate(entries)
    assert len(result) == 2


def test_dedup_preserves_unique():
    raw1 = "vless://uuid1@host1:443?type=tcp&security=reality#Server1"
    raw2 = "vless://uuid2@host2:8443?type=tcp&security=reality#Server2"
    entries = [
        ServerEntry(raw=raw1, protocol="vless", host="host1", port=443),
        ServerEntry(raw=raw2, protocol="vless", host="host2", port=8443),
    ]
    result = deduplicate(entries)
    assert len(result) == 2


def test_dedup_empty():
    assert deduplicate([]) == []


def test_dedup_same_base_different_name():
    base = "vless://uuid@host:443?type=tcp&security=reality"
    entries = [
        ServerEntry(raw=base + "#Name1", protocol="vless", host="host", port=443),
        ServerEntry(raw=base + "#Name2", protocol="vless", host="host", port=443),
    ]
    result = deduplicate(entries)
    assert len(result) == 1
