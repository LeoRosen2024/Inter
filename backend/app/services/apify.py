import hashlib
import re
from datetime import datetime
from typing import Any

from apify_client import ApifyClient
from sqlmodel import Session, select

from app.core.config import get_settings
from app.db import engine
from app.models import Reel, ReelMetricSnapshot, SocialProfile, SyncJob, utcnow


def value_from(item: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if isinstance(item, dict) and name in item:
            return item[name]
        value = getattr(item, name, None)
        if value is not None:
            return value
    return default


def integer_from(item: Any, *names: str) -> int:
    value = value_from(item, *names, default=0)
    try:
        return max(0, int(float(value or 0)))
    except (TypeError, ValueError):
        return 0


def datetime_from(item: Any, *names: str) -> datetime | None:
    value = value_from(item, *names)
    if isinstance(value, datetime):
        return value
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def stable_external_id(item: dict[str, Any]) -> str:
    external_id = value_from(item, "id", "shortCode", "shortcode", "videoId")
    if external_id:
        return str(external_id)
    source = str(value_from(item, "url", "postUrl", "videoUrl", default=item))
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:40]


def instagram_shortcode(url: str) -> str | None:
    match = re.search(r"/(?:reel|reels|p)/([A-Za-z0-9_-]+)", url)
    return match.group(1) if match else None


def normalized_title(item: dict[str, Any]) -> str:
    caption = str(value_from(item, "caption", "title", "text", default="Instagram Reel")).strip()
    first_line = caption.splitlines()[0].strip() if caption else "Instagram Reel"
    return first_line[:255] or "Instagram Reel"


def get_run_value(run: Any, dict_name: str, attribute_name: str) -> Any:
    if isinstance(run, dict):
        return run.get(dict_name) or run.get(attribute_name)
    return getattr(run, attribute_name, None) or getattr(run, dict_name, None)


def upsert_item(session: Session, item: dict[str, Any]) -> Reel:
    raw_handle = str(value_from(item, "ownerUsername", "username", "owner_username", default="unknown"))
    handle = raw_handle.strip().lstrip("@").lower() or "unknown"
    profile = session.exec(
        select(SocialProfile).where(
            SocialProfile.platform == "instagram",
            SocialProfile.handle == handle,
        )
    ).first()
    if profile is None:
        profile = SocialProfile(
            platform="instagram",
            role="competitor",
            handle=handle,
            display_name=str(value_from(item, "ownerFullName", "fullName", default=handle)),
            profile_url=f"https://www.instagram.com/{handle}/" if handle != "unknown" else None,
            followers_count=integer_from(item, "ownerFollowersCount", "followersCount"),
            total_views_count=integer_from(item, "ownerTotalViews", "totalViews"),
            engagement_rate=float(value_from(item, "engagementRate", default=0) or 0),
            raw_payload={"source": "apify"},
        )
        session.add(profile)
        session.flush()

    external_id = stable_external_id(item)
    reel = session.exec(
        select(Reel).where(Reel.profile_id == profile.id, Reel.external_id == external_id)
    ).first()
    if reel is None:
        reel = Reel(
            profile_id=profile.id,
            external_id=external_id,
            scope="trending",
            title=normalized_title(item),
        )

    reel.description = str(value_from(item, "caption", "text", default=""))
    reel.status = "online"
    reel.source_handle = f"@{handle}" if handle != "unknown" else "@instagram"
    reel.source_url = value_from(item, "url", "postUrl", "inputUrl")
    reel.media_url = value_from(item, "videoUrl", "video_url")
    reel.thumbnail_url = value_from(item, "displayUrl", "thumbnailUrl", "imageUrl")
    reel.duration_seconds = integer_from(item, "videoDuration", "duration")
    reel.views_count = integer_from(item, "videoPlayCount", "playCount", "viewsCount", "viewCount")
    reel.likes_count = integer_from(item, "likesCount", "likes")
    reel.comments_count = integer_from(item, "commentsCount", "comments")
    reel.trend_score = min(100.0, float(value_from(item, "trendScore", default=0) or 0))
    reel.published_at = datetime_from(item, "timestamp", "publishedAt", "takenAt")
    reel.raw_payload = item
    reel.updated_at = utcnow()
    session.add(reel)
    session.flush()

    session.add(
        ReelMetricSnapshot(
            reel_id=reel.id,
            views_count=reel.views_count,
            likes_count=reel.likes_count,
            comments_count=reel.comments_count,
        )
    )
    return reel


def process_sync_job(job_id: str) -> None:
    settings = get_settings()
    if not settings.apify_ready:
        raise RuntimeError("Apify integration is not configured")

    with Session(engine) as session:
        job = session.get(SyncJob, job_id)
        if job is None:
            return
        job.status = "running"
        job.started_at = utcnow()
        job.updated_at = utcnow()
        session.add(job)
        session.commit()

    try:
        token = settings.apify_token.get_secret_value() if settings.apify_token else ""
        client = ApifyClient(token)
        with Session(engine) as session:
            job = session.get(SyncJob, job_id)
            if job is None:
                return
            requested_limit = min(max(job.requested_limit, 1), 20)
            actor_input = dict(job.input_payload)
            if not actor_input:
                # Reuse a previously discovered owner when importing the same Reel again.
                shortcode = instagram_shortcode(job.source_url)
                owner = None
                if shortcode:
                    known = session.exec(
                        select(Reel).where(Reel.source_url.contains(shortcode))
                    ).first()
                    if known and known.profile_id:
                        owner_profile = session.get(SocialProfile, known.profile_id)
                        owner = owner_profile.handle if owner_profile else None
                actor_input = {"username": [owner or job.source_url], "resultsLimit": requested_limit}
            elif "directUrls" in actor_input and "username" not in actor_input:
                # The official actor accepts reel URLs in its required `username` array.
                actor_input["username"] = actor_input.pop("directUrls")
            actor_input["resultsLimit"] = min(int(actor_input.get("resultsLimit", requested_limit)), requested_limit)
            actor_input.setdefault("includeTranscript", False)
            actor_input.setdefault("includeDownloadedVideo", False)
            run = client.actor(job.actor_id).call(run_input=actor_input)
            if run is None:
                raise RuntimeError("Apify Actor did not return a run")

            run_id = str(get_run_value(run, "id", "id"))
            dataset_id = str(get_run_value(run, "defaultDatasetId", "default_dataset_id"))
            items = list(client.dataset(dataset_id).iterate_items())

            # A direct reel URL identifies the competitor. For a competitor import,
            # follow up with that profile so the requested 20 latest reels are loaded.
            if len(items) == 1 and requested_limit > 1:
                owner = value_from(items[0], "ownerUsername", "username", "owner_username")
                if owner:
                    profile_run = client.actor(job.actor_id).call(
                        run_input={"username": [str(owner)], "resultsLimit": requested_limit}
                    )
                    if profile_run is not None:
                        run_id = str(get_run_value(profile_run, "id", "id"))
                        dataset_id = str(get_run_value(profile_run, "defaultDatasetId", "default_dataset_id"))
                        items = list(client.dataset(dataset_id).iterate_items())

            job.run_id = run_id
            job.dataset_id = dataset_id
            job.updated_at = utcnow()
            session.add(job)
            session.commit()

            items = items[:requested_limit]
            for item in items:
                upsert_item(session, dict(item))

            job = session.get(SyncJob, job_id)
            if job is None:
                return
            job.status = "succeeded"
            job.result_count = len(items)
            job.finished_at = utcnow()
            job.updated_at = utcnow()
            session.add(job)
            session.commit()
    except Exception as exc:
        with Session(engine) as session:
            job = session.get(SyncJob, job_id)
            if job is not None:
                job.status = "failed"
                job.error_message = str(exc)[:2000]
                job.finished_at = utcnow()
                job.updated_at = utcnow()
                session.add(job)
                session.commit()
