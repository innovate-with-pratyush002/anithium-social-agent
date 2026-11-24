import asyncio
import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings
from app.db.session import AsyncSessionFactory, engine
from app.schemas.research_ingestion import ResearchIngestionRequest
from app.schemas.research_intelligence import ResearchIntelligenceRequest
from app.services.research_ingestion import ingest_research
from app.services.research_intelligence import (
    analyze_pending_research,
    get_research_analyzer,
)

settings = get_settings()
logger = logging.getLogger(__name__)


async def run_ingestion_job() -> None:
    try:
        async with AsyncSessionFactory() as session:
            result = await ingest_research(
                session,
                ResearchIngestionRequest(
                    max_items_per_source=settings.research_ingestion_max_items_per_source
                ),
            )
        logger.info(
            "Scheduled research ingestion completed: sources=%s fetched=%s "
            "created=%s duplicates=%s failed_sources=%s",
            result.sources_processed,
            result.fetched,
            result.created,
            result.duplicates,
            result.failed_sources,
        )
    except Exception:
        logger.exception("Scheduled research ingestion job failed")


async def run_analysis_job() -> None:
    try:
        analyzer = get_research_analyzer()
        async with AsyncSessionFactory() as session:
            result = await analyze_pending_research(
                session,
                ResearchIntelligenceRequest(
                    max_items=settings.research_analysis_max_items
                ),
                analyzer,
            )
        logger.info(
            "Scheduled research analysis completed: processed=%s analyzed=%s failed=%s",
            result.processed,
            result.analyzed,
            result.failed,
        )
    except Exception:
        logger.exception("Scheduled research analysis job failed")


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        run_ingestion_job,
        trigger="interval",
        minutes=settings.research_ingestion_interval_minutes,
        id="research-ingestion",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
        next_run_time=datetime.now(UTC),
    )
    scheduler.add_job(
        run_analysis_job,
        trigger="interval",
        minutes=settings.research_analysis_interval_minutes,
        id="research-analysis",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
        next_run_time=datetime.now(UTC),
    )
    return scheduler


async def main() -> None:
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    scheduler = create_scheduler()
    scheduler.start()
    logger.info(
        "Research worker started: ingestion every %s minutes; analysis every %s minutes",
        settings.research_ingestion_interval_minutes,
        settings.research_analysis_interval_minutes,
    )
    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown(wait=False)
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
