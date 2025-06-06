# StackForge

**StackForge** — mini-PaaS для деплоя Docker Compose стеков через API и web-dashboard.

Middle-grade pet project: auth, фоновые задачи, WebSocket-логи, метрики, миграции.

## Architecture

```
Client (TS dashboard) → FastAPI → PostgreSQL
                         ↓
                    Celery worker → docker compose
                         ↓
                    Redis (broker + pub/sub logs)
```

## Quick start

```bash
cp .env.example .env
docker compose up -d
cd backend && alembic upgrade head
uvicorn app.main:app --reload --port 8000
# frontend: open frontend/index.html or `python -m http.server 8080 -d frontend`
```

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/auth/register | регистрация |
| POST | /api/v1/auth/login | JWT |
| GET | /api/v1/stacks | список стеков |
| POST | /api/v1/stacks | создать стек |
| POST | /api/v1/stacks/{id}/deploy | запустить деплой |
| WS | /ws/deployments/{id} | live-логи |

## Stack

Python 3.11 · FastAPI · SQLAlchemy 2 · Celery · Redis · PostgreSQL · TypeScript

MIT

<!-- dashboard screenshot -->
