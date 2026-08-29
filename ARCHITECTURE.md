# Inter Reels backend architecture

## Request flow

```text
Browser frontend
    │  JSON over HTTP (/api/v1)
    ▼
Caddy reverse proxy
    │
    ▼
FastAPI
    ├── validates requests and exposes OpenAPI documentation
    ├── reads/writes SQLModel entities through a request-scoped session
    ├── creates Apify sync jobs without exposing the Apify token
    └── returns normalized numeric metrics to the frontend
             │
             ▼
        PostgreSQL
             ▲
             │
Apify worker ─┴── Apify Actor → Dataset items → idempotent upsert
```

## Data model

- `social_profiles`: own and competitor Instagram accounts.
- `reels`: normalized reel content and current metrics.
- `reel_scripts`: Hook, body and Call to Action with optimistic versioning.
- `reel_metric_snapshots`: metric history for later analytics.
- `tags` and `reel_tags`: normalized many-to-many tags.
- `sync_jobs`: queued/running/succeeded/failed Apify work with run and dataset IDs.
- `media_assets`: storage keys and metadata for covers, video, frames and exports.
- `app_settings`: profile and UI settings.

Raw Apify results are retained in the JSON payload of the matching reel for troubleshooting. Secrets are never stored in database rows.

## API surface

```text
GET    /api/v1/health/live
GET    /api/v1/health/ready
GET    /api/v1/reels?scope=trending|mine&limit=20
POST   /api/v1/reels
GET    /api/v1/reels/{id}
PATCH  /api/v1/reels/{id}
GET    /api/v1/reels/{id}/script
PUT    /api/v1/reels/{id}/script
GET    /api/v1/competitors
POST   /api/v1/competitors
GET    /api/v1/settings
PATCH  /api/v1/settings
GET    /api/v1/imports/apify/config
POST   /api/v1/imports/apify
GET    /api/v1/imports/{job_id}
```

Updates include a `version` number. A stale browser receives HTTP `409` instead of silently overwriting newer text.

## Apify lifecycle

1. The frontend submits an Instagram source URL to FastAPI.
2. FastAPI verifies that Apify is configured and inserts a `queued` sync job.
3. The worker claims one queued job and calls the configured Actor using the backend-only token.
4. The worker reads at most the requested number of dataset items.
5. Profiles and reels are upserted by stable external identifiers; metric snapshots are appended.
6. The job becomes `succeeded` or `failed`, and the frontend can read its status.

The Actor-specific input remains configurable because different Instagram Actors use different input schemas. Supplying the token and Actor ID is the only secret-bearing step left for the next integration phase.

## Deployment boundaries

- Cloudflare Pages serves only the static `frontend/` directory.
- Local Docker Compose and a future VPS run Caddy, FastAPI, worker and PostgreSQL.
- PostgreSQL has no public host port.
- Caddy and FastAPI share the edge network; only API, worker and migrations can reach the internal database network.
- Media files use a persistent Docker volume initially; an S3/R2 adapter can replace it later without changing database ownership.

