import asyncio
import pytest
from app.services.probe import probe_server


@pytest.mark.asyncio
async def test_probe_known_host():
    ok = await probe_server("1.1.1.1", 53, timeout=3)
    assert ok is True


@pytest.mark.asyncio
async def test_probe_unreachable():
    ok = await probe_server("192.0.2.1", 80, timeout=1)
    assert ok is False


@pytest.mark.asyncio
async def test_probe_closed_port():
    ok = await probe_server("127.0.0.1", 1, timeout=1)
    assert ok is False


@pytest.mark.asyncio
async def test_probe_empty_host():
    ok = await probe_server("", 80, timeout=1)
    assert ok is False


@pytest.mark.asyncio
async def test_probe_invalid_host():
    ok = await probe_server("invalid-host-that-does-not-exist.local", 80, timeout=1)
    assert ok is False
