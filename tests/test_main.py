import base64
from app.main import is_expired_subscription


def _encode(text: str) -> bytes:
    return base64.b64encode(text.encode())


def test_expired_all_zero():
    body = _encode(
        "vless://00000000-0000-0000-0000-000000000000@0.0.0.0:1?encryption=none&type=tcp&#⚠️ Приложение не поддерживается\n"
    )
    assert is_expired_subscription(body) is True


def test_expired_mixed_zero_and_normal():
    """If any line has a real UUID, sub is active."""
    body = _encode(
        "vless://00000000-0000-0000-0000-000000000000@0.0.0.0:1?type=tcp#⚠️ Приложение не поддерживается\n"
        "vless://real-uuid-here@host:443?type=tcp#Real Server\n"
    )
    assert is_expired_subscription(body) is False


def test_expired_all_zero_multiple():
    body = _encode(
        "vless://00000000-0000-0000-0000-000000000000@0.0.0.0:1?type=tcp#⚠️ Приложение не поддерживается\n"
        "vless://00000000-0000-0000-0000-000000000000@divider.local:443?type=tcp#Divider\n"
    )
    assert is_expired_subscription(body) is True


def test_expired_active_subscription():
    body = _encode(
        "vless://abc-123@host1:443?security=reality#Server1\n"
        "vless://def-456@host2:8443?security=tls#Server2\n"
    )
    assert is_expired_subscription(body) is False


def test_expired_empty():
    assert is_expired_subscription(b"") is False


def test_expired_invalid_base64():
    assert is_expired_subscription(b"not-valid-base64!!!") is False


def test_expired_no_protocol_lines():
    body = _encode("Just some text\nNo proxy links here\n")
    assert is_expired_subscription(body) is False
