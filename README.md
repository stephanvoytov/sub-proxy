# Sub-Proxy

[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/stephanvoytov/sub-proxy/tests.yml?label=tests)](https://github.com/stephanvoytov/sub-proxy/actions)
[![GitHub stars](https://img.shields.io/github/stars/stephanvoytov/sub-proxy?style=flat)](https://github.com/stephanvoytov/sub-proxy/stargazers)
[![Docker Pulls](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://github.com/stephanvoytov/sub-proxy/pkgs/container/sub-proxy)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)

Subscription proxy server for Remnawave and other panels. Merges external server sources into user subscriptions with deduplication, grouping, and optional ping checking.

[Читать на русском](README.ru.md)

## Features

- Proxies subscription requests to any backend (Remnawave, custom)
- Merges servers from multiple custom sources into the subscription
- Groups servers by source with labeled dividers
- Deduplicates across all sources and the original subscription
- Optional async ping probing for each server
- Configurable cache refresh interval
- REST API for status and manual refresh

## Quick Start

1. Clone the repo and copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

2. Edit `.env` with your backend URL and sources:

```env
BACKEND_URL=http://remnawave:3000

SOURCE_1_LABEL=🇷🇺 Russia
SOURCE_1_URL=https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt
SOURCE_1_COUNT=10
```

3. Run with Docker Compose:

```bash
docker compose up -d
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/{path}` | Transparent proxy: forwards any path to backend, merges subscription responses |
| GET | `/health` | Health check |
| GET | `/api/status` | Cache and source status |
| GET | `/api/refresh` | Force cache refresh |

## Architecture

Sub-Proxy sits between the subscription page and the backend:

```
User → Subscription Page → Sub-Proxy → Backend
```

The subscription page sends all requests to Sub-Proxy (via `REMNAWAVE_PANEL_URL`).  
Sub-Proxy forwards them to the backend, and when a subscription response is detected (base64-encoded proxy links), it merges cached servers from configured sources before returning.

No Caddy or reverse proxy changes are needed — Sub-Proxy stays internal to the Docker network.

## Configuring for Remnawave

1. Make sure Sub-Proxy is on the same Docker network as Remnawave (e.g. `remnawave-network`):

```yaml
services:
  sub-proxy:
    build: .
    container_name: sub-proxy
    networks:
      - remnawave-network

networks:
  remnawave-network:
    external: true
```

2. In the subscription page `.env`, change the panel URL:

```diff
- REMNAWAVE_PANEL_URL=http://remnawave:3000
+ REMNAWAVE_PANEL_URL=http://sub-proxy:4080
```

3. Restart the subscription page container:

```bash
docker compose restart remnawave-subscription-page
```

That's it. Sub-Proxy intercepts subscription requests, adds servers from configured sources, and passes everything else through unchanged.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | — | Backend base URL (e.g. Remnawave panel) |
| `SOURCE_{ID}_LABEL` | — | Source group display name |
| `SOURCE_{ID}_URL` | — | Source URL (GitHub raw, HTTP sub, etc.) |
| `SOURCE_{ID}_COUNT` | `10` | Max servers from this source |
| `SOURCE_{ID}_PROBE` | `false` | Enable ping check for this source |
| `REFRESH_INTERVAL` | `900` | Cache refresh interval (seconds) |
| `DEDUP_ENABLED` | `true` | Remove duplicate servers |
| `PROBE_TIMEOUT` | `1.5` | Ping timeout (seconds) |
| `PROBE_CONCURRENCY` | `12` | Concurrent ping checks |

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run locally
uvicorn app.main:app --reload --port 4080
```

## License

MIT
