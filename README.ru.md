# Sub-Proxy

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
| GET | `/{short_uuid}` | Получить подписку |
| GET | `/health` | Health check |
| GET | `/api/status` | Статус кеша и источников |
| GET | `/api/refresh` | Принудительный рефреш кеша |

## Интеграция с Caddy

Добавьте в Caddyfile:

```caddyfile
your-domain.com {
    handle /sub* {
        reverse_proxy sub-proxy:4080
    }
}
```

## Пример конфига для MilkyNet

```env
BACKEND_TYPE=remnawave
BACKEND_URL=http://remnawave:3000
BACKEND_API_TOKEN=eyJhbGciOiJIUzI1NiIs...

SOURCE_1_LABEL=🆓 Бесплатные серверы (проверьте пинг)
SOURCE_1_URL=https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt
SOURCE_1_COUNT=10
SOURCE_1_PROBE=false

SOURCE_2_LABEL=⚡ Премиум серверы
SOURCE_2_URL=https://example.com/my-premium-servers.txt
SOURCE_2_COUNT=20
SOURCE_2_PROBE=true
```

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
