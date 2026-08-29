import logging
import time

from sqlalchemy import Select
from sqlmodel import Session, select

from app.core.config import get_settings
from app.db import engine
from app.models import SyncJob
from app.services.apify import process_sync_job


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("inter.worker")


def claim_job() -> str | None:
    with Session(engine) as session:
        statement: Select = select(SyncJob).where(SyncJob.status == "queued").order_by(SyncJob.created_at).limit(1)
        if engine.dialect.name == "postgresql":
            statement = statement.with_for_update(skip_locked=True)
        job = session.exec(statement).first()
        if job is None:
            return None
        job.status = "claimed"
        session.add(job)
        session.commit()
        return job.id


def main() -> None:
    settings = get_settings()
    logger.info("Inter Apify worker started")
    while True:
        job_id = claim_job()
        if job_id:
            logger.info("Processing sync job %s", job_id)
            process_sync_job(job_id)
        else:
            time.sleep(max(1, settings.apify_poll_interval_seconds))


if __name__ == "__main__":
    main()

