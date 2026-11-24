from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from app.services.research_quality import calculate_research_quality


def test_quality_score_rewards_complete_recent_research_from_reliable_source() -> None:
    now = datetime(2026, 11, 24, tzinfo=UTC)
    item = SimpleNamespace(
        title="A detailed update about modern AI coding agents",
        url="https://example.com/ai-agents",
        summary="A " * 180,
        content="Article body " * 100,
        published_at=now - timedelta(days=2),
    )

    score, signals = calculate_research_quality(item, source_reliability=0.95, now=now)

    assert score == 0.99
    assert "descriptive_title" in signals
    assert "detailed_summary" in signals
    assert "full_text_available" in signals
    assert "published_within_7_days" in signals
    assert "high_source_reliability" in signals


def test_quality_score_is_lower_for_thin_research_and_unreliable_source() -> None:
    now = datetime(2026, 11, 24, tzinfo=UTC)
    item = SimpleNamespace(
        title="AI",
        url=None,
        summary=None,
        content=None,
        published_at=now - timedelta(days=500),
    )

    score, signals = calculate_research_quality(item, source_reliability=0.1, now=now)

    assert score == 0.1
    assert "missing_article_url" in signals
    assert "missing_summary" in signals
    assert "no_article_text" in signals
    assert "older_than_one_year" in signals
    assert "low_source_reliability" in signals
