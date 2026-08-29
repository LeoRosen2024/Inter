# Inter Reels

Inter Reels is a German-language dashboard with a real API and database foundation.

## Architecture

- `frontend/` — responsive HTML/CSS/JavaScript client.
- `backend/` — FastAPI REST API, SQLModel domain models and Alembic migrations.
- PostgreSQL — profiles, reels, scripts, metrics, settings, import jobs and media metadata.
- `worker` — database-backed background worker prepared for Apify Actor runs.
- Caddy — serves the frontend and proxies `/api/*` to FastAPI in the local/VPS stack.

The detailed request and data flow is documented in [ARCHITECTURE.md](ARCHITECTURE.md).

## Start locally

1. Make sure Docker Desktop is running.
2. Copy `.env.example` to `.env`.
3. Replace `POSTGRES_PASSWORD` in `.env` with a long random local password.
4. Start the complete stack:

```text
docker compose up -d --build
```

Open:

- Application: `http://127.0.0.1:8080/`
- API readiness: `http://127.0.0.1:8080/api/v1/health/ready`
- Interactive API documentation: `http://127.0.0.1:8080/api/docs`

The first start applies Alembic migrations and seeds 20 trending reels, 20 own reels and 20 competitors. Data is persisted in the `inter_postgres-data` Docker volume.

## Apify

The integration adapter and background job flow are already present, but disabled by default. Put the values only in `.env` on the backend host:

```text
APIFY_ENABLED=true
APIFY_TOKEN=...
APIFY_ACTOR_ID=...
```

Never add the token to `frontend/config.js`, Git, GitHub variables intended for the browser, or screenshots. The browser creates an import job; the worker calls Apify and stores normalized results in PostgreSQL.

## Cloudflare Pages

`wrangler.jsonc` limits the Pages output to `frontend/`, so backend source files and environment configuration are not published. Until a public API host is connected, the Pages site remains in a clearly marked demo mode. FastAPI and PostgreSQL run locally now and can later move unchanged to a VPS.

## Backend tests

```text
cd backend
python -m pip install -e ".[test]"
python -m pytest
alembic upgrade head
alembic check
```

