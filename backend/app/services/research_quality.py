from datetime import UTC, datetime, timedelta

from app.models.research_item import ResearchItem


def calculate_research_quality(
    item: ResearchItem,
    source_reliability: float = 0.7,
    now: datetime | None = None,
) -> tuple[float, list[str]]:
    """Calculate an explainable 0..1 quality score from available research metadata."""
    current_time = now or datetime.now(UTC)
    score = 0.0
    signals: list[str] = []

    if len(item.title.strip()) >= 20:
        score += 0.15
        signals.append("descriptive_title")
    elif item.title.strip():
        score += 0.08
        signals.append("short_title")
    else:
        signals.append("missing_title")

    if item.url:
        score += 0.10
        signals.append("article_url_available")
    else:
        signals.append("missing_article_url")

    summary_length = len((item.summary or "").strip())
    if summary_length >= 300:
        score += 0.25
        signals.append("detailed_summary")
    elif summary_length >= 80:
        score += 0.18
        signals.append("usable_summary")
    elif summary_length > 0:
        score += 0.08
        signals.append("short_summary")
    else:
        signals.append("missing_summary")

    content_length = len((item.content or "").strip())
    if content_length >= 1000:
        score += 0.15
        signals.append("full_text_available")
    elif content_length >= 200:
        score += 0.10
        signals.append("partial_text_available")
    else:
        signals.append("no_article_text")

    published_at = item.published_at
    if published_at is None:
        score += 0.075
        signals.append("publication_date_unknown")
    else:
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=UTC)
        age = current_time - published_at.astimezone(UTC)
        if age <= timedelta(days=7):
            score += 0.15
            signals.append("published_within_7_days")
        elif age <= timedelta(days=30):
            score += 0.12
            signals.append("published_within_30_days")
        elif age <= timedelta(days=90):
            score += 0.08
            signals.append("published_within_90_days")
        elif age <= timedelta(days=365):
            score += 0.04
            signals.append("published_within_year")
        else:
            signals.append("older_than_one_year")

    reliability = min(1.0, max(0.0, source_reliability))
    score += 0.20 * reliability
    if reliability >= 0.8:
        signals.append("high_source_reliability")
    elif reliability >= 0.6:
        signals.append("medium_source_reliability")
    else:
        signals.append("low_source_reliability")

    return round(min(1.0, score), 3), signals


__all__ = ["calculate_research_quality"]
