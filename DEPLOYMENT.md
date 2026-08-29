# Inter deployment

## Current environments

- Cloudflare Pages publishes only `frontend/` and therefore runs in demo mode until a public API is connected.
- The complete application runs locally at `http://127.0.0.1:8080` through Docker Compose.
- A future VPS checkout remains `/opt/inter` and uses the same Compose stack.

## One-time local setup

1. Start Docker Desktop.
2. Copy `.env.example` to `.env`.
3. Set a unique `POSTGRES_PASSWORD`.
4. Run `docker compose up -d --build`.
5. Verify the page, `/api/v1/health/ready`, and `/api/docs` through port `8080`.

Do not commit `.env`. Do not use `docker compose down -v` unless the database and media volumes are intentionally being deleted.

## Server prerequisites

- Linux VPS with SSH access for a non-root deployment user.
- Git and Docker Engine with the Compose plugin.
- `/opt/inter` owned by the deployment user.
- Read-only GitHub deploy key for `LeoRosen2024/Inter`.
- Server-only `/opt/inter/.env` with a strong database password and allowed origins.

Apify secrets belong only in `/opt/inter/.env` or a server secret manager:

```text
APIFY_ENABLED=true
APIFY_TOKEN=...
APIFY_ACTOR_ID=...
```

## GitHub Actions deployment

The existing deployment workflow is inactive until repository variable `DEPLOY_ENABLED=true` is set. Configure these `production` environment secrets first:

- `DEPLOY_HOST`
- `DEPLOY_PORT`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`
- `DEPLOY_KNOWN_HOSTS`

Every enabled `main` deployment performs a fast-forward-only pull, builds the images, applies migrations, recreates the project containers and verifies both frontend and API readiness.

## Backups

Before a destructive migration or Docker-volume change, back up PostgreSQL and the `media-data` volume. Normal deployments must never remove either volume.

