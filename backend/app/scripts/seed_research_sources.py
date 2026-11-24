"""Idempotently seed the initial trusted RSS source catalog.

Run from the backend container:
    python -m app.scripts.seed_research_sources

Existing source records are intentionally left unchanged so administrator
edits to reliability scores, descriptions, or activation state are preserved.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionFactory, engine
from app.models.source import Source
from app.models.user import User

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ResearchSourceDefinition:
    name: str
    url: str
    description: str
    reliability_score: float
    config: dict[str, Any]


SOURCE_CATALOG = (
    ResearchSourceDefinition(
        name="OpenAI News",
        url="https://openai.com/news/rss.xml",
        description="Official OpenAI product, research, safety, and company announcements.",
        reliability_score=0.95,
        config={"topics": ["ai", "models", "research", "product"], "source_kind": "official"},
    ),
    ResearchSourceDefinition(
        name="Google DeepMind Blog",
        url="https://deepmind.google/blog/rss.xml",
        description="Official Google DeepMind research and model announcements.",
        reliability_score=0.95,
        config={"topics": ["ai", "research", "models"], "source_kind": "official"},
    ),
    ResearchSourceDefinition(
        name="Google Research Blog",
        url="https://research.google/blog/rss/",
        description="Official Google Research articles, projects, and research updates.",
        reliability_score=0.95,
        config={"topics": ["ai", "research", "engineering"], "source_kind": "official"},
    ),
    ResearchSourceDefinition(
        name="Google AI Blog",
        url="https://blog.google/technology/ai/rss/",
        description="Official Google AI product and technology announcements.",
        reliability_score=0.95,
        config={"topics": ["ai", "products", "models"], "source_kind": "official"},
    ),
    ResearchSourceDefinition(
        name="Hugging Face Blog",
        url="https://huggingface.co/blog/feed.xml",
        description="Hugging Face updates on open models, datasets, libraries, and tooling.",
        reliability_score=0.90,
        config={"topics": ["open-source-ai", "models", "tools", "datasets"], "source_kind": "official"},
    ),
    ResearchSourceDefinition(
        name="NVIDIA Blog",
        url="https://blogs.nvidia.com/feed/",
        description="Official NVIDIA announcements and articles across AI, computing, and software.",
        reliability_score=0.90,
        config={"topics": ["ai", "hardware", "software", "computing"], "source_kind": "official"},
    ),
    ResearchSourceDefinition(
        name="arXiv Artificial Intelligence",
        url="https://rss.arxiv.org/rss/cs.AI",
        description="Research preprints in the arXiv Artificial Intelligence category.",
        reliability_score=0.90,
        config={"topics": ["ai", "research", "papers"], "source_kind": "research_repository"},
    ),
    ResearchSourceDefinition(
        name="arXiv Machine Learning",
        url="https://rss.arxiv.org/rss/cs.LG",
        description="Research preprints in the arXiv Machine Learning category.",
        reliability_score=0.90,
        config={"topics": ["machine-learning", "research", "papers"], "source_kind": "research_repository"},
    ),
)


async def seed_research_sources(session: AsyncSession) -> tuple[int, int]:
    """Insert missing catalog entries and return (created, already_present)."""
    admin_id = await session.scalar(
        select(User.id)
        .where(User.is_admin.is_(True), User.is_active.is_(True))
        .order_by(User.created_at.asc())
        .limit(1)
    )
    if admin_id is None:
        raise RuntimeError(
            "No active administrator exists. Register an account and promote it "
            "to admin before seeding research sources."
        )

    catalog_urls = [definition.url for definition in SOURCE_CATALOG]
    existing_urls = set(
        (
            await session.scalars(
                select(Source.url).where(Source.url.in_(catalog_urls))
            )
        ).all()
    )

    missing = [
        definition
        for definition in SOURCE_CATALOG
        if definition.url not in existing_urls
    ]
    for definition in missing:
        session.add(
            Source(
                name=definition.name,
                source_type="rss",
                url=definition.url,
                description=definition.description,
                config=definition.config,
                reliability_score=definition.reliability_score,
                is_active=True,
                created_by_id=admin_id,
            )
        )

    if missing:
        await session.commit()

    created = len(missing)
    already_present = len(SOURCE_CATALOG) - created
    return created, already_present


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    try:
        async with AsyncSessionFactory() as session:
            created, already_present = await seed_research_sources(session)
        logger.info(
            "Research source catalog ready: created=%s already_present=%s total=%s",
            created,
            already_present,
            len(SOURCE_CATALOG),
        )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
