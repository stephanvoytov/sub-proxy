# Sub-Proxy

[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/stephanvoytov/sub-proxy/tests.yml?label=тесты)](https://github.com/stephanvoytov/sub-proxy/actions)
[![GitHub stars](https://img.shields.io/github/stars/stephanvoytov/sub-proxy?style=flat)](https://github.com/stephanvoytov/sub-proxy/stargazers)
[![Docker Pulls](https://img.shields.io/badge/docker-готово-blue?logo=docker)](https://github.com/stephanvoytov/sub-proxy/pkgs/container/sub-proxy)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)

Прокси-сервер подписок для Remnawave и других панелей. Подмешивает серверы из внешних источников в подписку пользователя с группировкой, дедупликацией и опциональной проверкой пинга.

## Возможности

- Проксирует запросы подписок к любому бекенду (Remnawave, custom)
- Подмешивает серверы из нескольких кастомных источников
- Группирует серверы по источникам с разделителями
- Удаляет дубликаты между источниками и оригинальной подпиской
- Опциональная асинхронная проверка пинга
- Настраиваемый интервал обновления кеша
- REST API для статуса и принудительного рефреша

## Быстрый старт

1. Клонируйте репозиторий и скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

2. Отредактируйте `.env`:

```env
BACKEND_TYPE=remnawave
BACKEND_URL=http://remnawave:3000
BACKEND_API_TOKEN=your_token

SOURCE_1_LABEL=🇷🇺 Russia Yandex
SOURCE_1_URL=https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt
SOURCE_1_COUNT=10
```

3. Запустите с Docker Compose:

```bash
docker compose up -d
```

## Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/{path}` | Прозрачный прокси: любой путь, подписки с подмешиванием |
| GET | `/health` | Health check |
| GET | `/api/status` | Статус кеша и источников |
| GET | `/api/refresh` | Принудительный рефреш кеша |

## Архитектура

Sub-Proxy располагается между subscription page и бекендом:

```
Пользователь → Subscription Page → Sub-Proxy → Backend
```

Subscription page отправляет все запросы на Sub-Proxy (через `REMNAWAVE_PANEL_URL`).  
Sub-Proxy проксирует их в бекенд, а когда обнаруживает subscription-ответ (base64 с proxy ссылками) — подмешивает закешированные серверы из настроенных источников.

Никаких изменений в Caddy или reverse proxy не требуется — Sub-Proxy работает внутри Docker сети.

## Настройка для Remnawave

1. Убедитесь, что Sub-Proxy в той же Docker сети, что и Remnawave (например `remnawave-network`):

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

2. В `.env` subscription page измените URL панели:

```diff
- REMNAWAVE_PANEL_URL=http://remnawave:3000
+ REMNAWAVE_PANEL_URL=http://sub-proxy:4080
```

3. Перезапустите subscription page:

```bash
docker compose restart remnawave-subscription-page
```

Готово. Sub-Proxy перехватывает subscription-запросы, подмешивает серверы из источников, всё остальное пропускает без изменений.

## Конфигурация

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `BACKEND_TYPE` | `remnawave` | Тип бекенда (`remnawave` или `simple`) |
| `BACKEND_URL` | — | Базовый URL бекенда |
| `BACKEND_API_TOKEN` | — | API токен для бекенда |
| `SOURCE_{ID}_LABEL` | — | Название группы источников |
| `SOURCE_{ID}_URL` | — | URL источника (GitHub raw, HTTP подписка и т.д.) |
| `SOURCE_{ID}_COUNT` | `10` | Максимум серверов из этого источника |
| `SOURCE_{ID}_PROBE` | `false` | Включить проверку пинга |
| `REFRESH_INTERVAL` | `900` | Интервал обновления кеша (сек) |
| `DEDUP_ENABLED` | `true` | Удалять дубликаты серверов |
| `PROBE_TIMEOUT` | `1.5` | Таймаут проверки пинга (сек) |
| `PROBE_CONCURRENCY` | `12` | Количество одновременных проверок пинга |

## Разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск тестов
pytest tests/ -v

# Локальный запуск
uvicorn app.main:app --reload --port 4080
```

## Лицензия

MIT
