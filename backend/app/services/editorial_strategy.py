from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_draft import ContentDraft
from app.models.research_item import ResearchItem
from app.schemas.common import PageMeta
from app.schemas.editorial import (
    ContentOpportunity,
    EditorialOpportunitiesResponse,
    PlatformOpportunity,
)

_PLATFORM_ANGLES = {
    "linkedin": {
        "angle": (
            "Translate the development into practical implications for developers "
            "and technology teams."
        ),
        "suggested_format": "insight_post",
        "rationale": "Professional context and actionable implications suit a LinkedIn discussion.",
    },
    "instagram": {
        "angle": "Break the development into a simple visual explanation with one clear takeaway.",
        "suggested_format": "educational_carousel",
        "rationale": "A visual, saveable explanation makes technical information easier to scan.",
    },
    "x": {
        "angle": (
            "Lead with the most useful verified takeaway, then add concise context "
            "and implications."
        ),
        "suggested_format": "short_post_or_thread",
        "rationale": (
            "A concise hook and focused follow-up points suit fast-moving "
            "X conversations."
        ),
    },
}


def _opportunity_score(item: ResearchItem, now: datetime) -> float:
    relevance = item.relevance_score if item.relevance_score is not None else 0.0
    quality = item.quality_score if item.quality_score is not None else 0.5
    discovered = item.discovered_at
    if discovered.tzinfo is None:
        discovered = discovered.replace(tzinfo=UTC)
    age_days = max((now - discovered).total_seconds() / 86400, 0)
    freshness = max(0.0, 1.0 - age_days / 30.0)
    return round(min(max(0.6 * relevance + 0.25 * quality + 0.15 * freshness, 0), 1), 3)


def _opportunity_reason(item: ResearchItem, score: float) -> str:
    signals: list[str] = []
    if (item.relevance_score or 0) >= 0.7:
        signals.append("strong technology relevance")
    if (item.quality_score or 0) >= 0.7:
        signals.append("useful source detail")
    if item.published_at is not None:
        signals.append("source includes a publication date")
    if not signals:
        signals.append("a research item is available for editorial review")
    return f"Suggested because of {', '.join(signals)} (editorial score {score:.3f})."


async def get_content_opportunities(
    session: AsyncSession,
    *,
    platforms: Sequence[str] = ("linkedin", "instagram", "x"),
    window_days: int = 14,
    limit: int = 20,
    now: datetime | None = None,
) -> EditorialOpportunitiesResponse:
    current_time = now or datetime.now(UTC)
    cutoff = current_time - timedelta(days=window_days)
    items = list(
        (
            await session.scalars(
                select(ResearchItem)
                .where(
                    ResearchItem.analysis_status == "completed",
                    ResearchItem.status == "new",
                    ResearchItem.discovered_at >= cutoff,
                )
                .order_by(ResearchItem.discovered_at.desc())
            )
        ).all()
    )
    if not items:
        return EditorialOpportunitiesResponse(
            items=[], pagination=PageMeta(total=0, limit=limit, offset=0), window_days=window_days
        )

    item_ids = [item.id for item in items]
    existing_drafts = (
        await session.execute(
            select(ContentDraft.research_item_id, ContentDraft.platform).where(
                ContentDraft.research_item_id.in_(item_ids)
            )
        )
    ).all()
    drafted_platforms: dict[UUID, set[str]] = {}
    for research_item_id, platform in existing_drafts:
        if research_item_id is not None:
            drafted_platforms.setdefault(research_item_id, set()).add(platform)

    requested_platforms = list(dict.fromkeys(platforms))
    opportunities: list[ContentOpportunity] = []
    for item in items:
        available = [
            PlatformOpportunity(platform=platform, **_PLATFORM_ANGLES[platform])
            for platform in requested_platforms
            if platform not in drafted_platforms.get(item.id, set())
        ]
        if not available:
            continue
        score = _opportunity_score(item, current_time)
        opportunities.append(
            ContentOpportunity(
                research_item_id=item.id,
                title=item.title,
                topic=item.topic,
                summary=item.summary,
                relevance_score=item.relevance_score,
                quality_score=item.quality_score,
                opportunity_score=score,
                opportunity_reason=_opportunity_reason(item, score),
                available_platforms=available,
            )
        )

    opportunities.sort(key=lambda opportunity: opportunity.opportunity_score, reverse=True)
    selected = opportunities[:limit]
    return EditorialOpportunitiesResponse(
        items=selected,
        pagination=PageMeta(total=len(opportunities), limit=limit, offset=0),
        window_days=window_days,
    )
