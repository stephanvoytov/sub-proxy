import pytest
from app.services.parser import parse_config


def test_parse_vless_reality():
    raw = "vless://ae5ba4be-7262-4199-bd62-210ed8999b9f@2.59.43.249:5443?type=tcp&security=reality&flow=xtls-rprx-vision&fp=chrome&pbk=LGcG8Sqv5vPDypbaEgHV0ZGqQOBkgDepPWXyDohbVXQ&sni=max.ru#🇫🇮 Finland | 🌐 [*CIDR]"
    entry = parse_config(raw)
    assert entry is not None
    assert entry.protocol == "vless"
    assert entry.host == "2.59.43.249"
    assert entry.port == 5443
    assert entry.uuid == "ae5ba4be-7262-4199-bd62-210ed8999b9f"
    assert entry.security == "reality"
    assert "Finland" in entry.name


def test_parse_vless_reality_yandex():
    raw = "vless://1b9e301d-cecd-4eb1-8b36-eef811c2696d@ru7.vitok.cc:443?type=tcp&security=reality&fp=chrome&pbk=eXl8Dpux23etQ0aA_16LUQ9eBwfDqbCaJm7YusDIzUU&sid=5e841fab&sni=ads.x5.ru#🇫🇮 Finland [*CIDR] YA"
    entry = parse_config(raw)
    assert entry is not None
    assert entry.protocol == "vless"
    assert entry.host == "ru7.vitok.cc"
    assert entry.port == 443
    assert entry.security == "reality"


def test_parse_vless_tls():
    raw = "vless://931729a8-3c20-4841-89a1-f18dc9ce0a6f@213.171.30.187:8443?encryption=none&type=tcp&security=tls&fp=chrome&sni=cdn3-87.vk-cdnvideo.com#🇳🇱 The Netherlands | 🌐 [*CIDR]"
    entry = parse_config(raw)
    assert entry is not None
    assert entry.protocol == "vless"
    assert entry.host == "213.171.30.187"
    assert entry.port == 8443
    assert entry.security == "tls"


def test_parse_trojan():
    raw = "trojan://humanity@216.24.57.7:443?path=%2Fassignment&security=tls&insecure=0&host=www.ignitelimit.com&type=ws&allowInsecure=0&sni=www.ignitelimit.com#🇫🇷 France [*CIDR]"
    entry = parse_config(raw)
    assert entry is not None
    assert entry.protocol == "trojan"
    assert entry.host == "216.24.57.7"
    assert entry.port == 443


def test_parse_vless_nosecurity():
    raw = "vless://48cdcfef-af9c-4eff-888c-cace67ae5881@107.161.168.212:56947?encryption=none&security=none&type=tcp#🇺🇸 United States [*CIDR]"
    entry = parse_config(raw)
    assert entry is not None
    assert entry.protocol == "vless"
    assert entry.host == "107.161.168.212"
    assert entry.port == 56947
    assert entry.security == "none"


def test_parse_vless_grpc():
    raw = "vless://a1b19834-a5e3-4d49-9301-aaa3fb248f49@185.14.46.20.blanesik.space:443?mode=gun&security=tls&encryption=none&alpn=h2&authority=grpc.vhub.pro&fp=chrome&allowinsecure=0&type=grpc&serviceName=%2Fsequre%2Fgrpc&sni=185.14.46.20.blanesik.space#🇷🇺 Russia [*CIDR]"
    entry = parse_config(raw)
    assert entry is not None
    assert entry.protocol == "vless"
    assert entry.host == "185.14.46.20.blanesik.space"
    assert entry.port == 443
    assert entry.network == "grpc"


def test_parse_invalid_link():
    assert parse_config("") is None
    assert parse_config("not-a-link") is None
    assert parse_config("://missing-protocol") is None


def test_parse_no_name():
    raw = "vless://ae5ba4be-7262-4199-bd62-210ed8999b9f@2.59.43.249:5443?type=tcp&security=reality"
    entry = parse_config(raw)
    assert entry is not None
    assert entry.port == 5443
