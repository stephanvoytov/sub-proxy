# Sub-Proxy

Subscription proxy server for Remnawave and other panels. Merges external server sources into user subscriptions with deduplication, grouping, and optional ping checking.

## Features

- Proxies subscription requests to any backend (Remnawave, custom)
- Merges servers from multiple custom sources into the subscription
- Groups servers by source with labeled dividers
- Deduplicates across all sources and the original subscription
- Optional async ping probing for each server
- Configurable refresh interval
- REST API for status and manual refresh

## Quick Start

1. Clone the repo and copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

2. Edit `.env` with your backend URL and sources:

```env
BACKEND_TYPE=remnawave
BACKEND_URL=http://remnawave:3000
BACKEND_API_TOKEN=your_token

SOURCE_1_LABEL=🇷🇺 Russia
SOURCE_1_URL=https://raw.githubusercontent.com/.../configs.txt
SOURCE_1_COUNT=10
```

3. Run with Docker Compose:

```bash
docker compose up -d
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/{short_uuid}` | Get merged subscription |
| GET | `/health` | Health check |
| GET | `/api/status` | Cache and source status |
| GET | `/api/refresh` | Force cache refresh |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_TYPE` | `remnawave` | Backend type (`remnawave` or `simple`) |
| `BACKEND_URL` | - | Backend base URL |
| `BACKEND_API_TOKEN` | - | API token for backend |
| `SOURCE_{ID}_LABEL` | - | Source group display name |
| `SOURCE_{ID}_URL` | - | Source URL (GitHub raw, HTTP, etc.) |
| `SOURCE_{ID}_COUNT` | `10` | Max servers from this source |
| `SOURCE_{ID}_PROBE` | `false` | Enable ping check for this source |
| `REFRESH_INTERVAL` | `900` | Cache refresh interval in seconds |
| `DEDUP_ENABLED` | `true` | Remove duplicate servers |

## License

MIT
