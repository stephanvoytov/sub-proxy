import os
from app.config import Settings


def test_default_values():
    s = Settings(
        BACKEND_URL="http://test:3000",
        BACKEND_API_TOKEN="token123",
        SOURCE_1_LABEL="Test",
        SOURCE_1_URL="http://example.com/configs.txt",
    )
    assert s.BACKEND_TYPE == "remnawave"
    assert s.REFRESH_INTERVAL == 900
    assert s.DEDUP_ENABLED is True


def test_sources_property():
    s = Settings(
        BACKEND_URL="http://test:3000",
        BACKEND_API_TOKEN="token123",
        SOURCE_1_LABEL="🇷🇺 Russia",
        SOURCE_1_URL="http://example.com/rus.txt",
        SOURCE_1_COUNT=10,
        SOURCE_2_LABEL="🌍 World",
        SOURCE_2_URL="http://example.com/world.txt",
        SOURCE_2_COUNT=5,
    )
    sources = s.sources
    assert len(sources) == 2
    assert sources[0].label == "🇷🇺 Russia"
    assert sources[0].count == 10
    assert sources[1].label == "🌍 World"
    assert sources[1].count == 5


def test_sources_empty():
    s = Settings(
        BACKEND_URL="http://test:3000",
        BACKEND_API_TOKEN="token123",
    )
    assert s.sources == []


def test_sources_partial_config():
    s = Settings(
        BACKEND_URL="http://test:3000",
        BACKEND_API_TOKEN="token123",
        SOURCE_1_LABEL="Only Label",
    )
    # URL is empty, so source should not appear
    assert len(s.sources) == 0


def test_source_probe_default():
    s = Settings(
        BACKEND_URL="http://test:3000",
        BACKEND_API_TOKEN="token123",
        SOURCE_1_LABEL="Test",
        SOURCE_1_URL="http://example.com/test.txt",
    )
    assert s.sources[0].probe is False


def test_source_squads_empty_by_default():
    s = Settings(
        BACKEND_URL="http://test:3000",
        BACKEND_API_TOKEN="token123",
        SOURCE_1_LABEL="Test",
        SOURCE_1_URL="http://example.com/test.txt",
    )
    assert s.sources[0].squads == []


def test_source_squads_parsed():
    s = Settings(
        BACKEND_URL="http://test:3000",
        BACKEND_API_TOKEN="token123",
        SOURCE_1_LABEL="Test",
        SOURCE_1_URL="http://example.com/test.txt",
        SOURCE_1_SQUADS="abc123,def456",
    )
    assert s.sources[0].squads == ["abc123", "def456"]


def test_source_squads_single_value():
    s = Settings(
        BACKEND_URL="http://test:3000",
        BACKEND_API_TOKEN="token123",
        SOURCE_1_LABEL="Test",
        SOURCE_1_URL="http://example.com/test.txt",
        SOURCE_1_SQUADS="abc123",
    )
    assert s.sources[0].squads == ["abc123"]
