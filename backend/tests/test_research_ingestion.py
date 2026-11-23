from httpx import AsyncClient

from app.services import research_ingestion

RSS_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Example Tech</title>
<item><title>AI Agents Update</title><link>https://news.example.com/ai-agents</link>
<description><![CDATA[<p>AI agents are changing software workflows.</p>]]></description>
<pubDate>Mon, 23 Nov 2026 10:00:00 GMT</pubDate>
<category>AI</category></item>
</channel></rss>"""


async def _create_rss_source(client: AsyncClient) -> str:
    response = await client.post(
        "/api/v1/sources",
        json={
            "name": "Example Tech RSS",
            "source_type": "rss",
            "url": "https://news.example.com/feed.xml",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


async def test_rss_ingestion_creates_research_items_and_deduplicates(
    client: AsyncClient,
    monkeypatch,
) -> None:
    source_id = await _create_rss_source(client)

    async def fake_download(url: str) -> bytes:
        assert url == "https://news.example.com/feed.xml"
        return RSS_FEED

    monkeypatch.setattr(research_ingestion, "_download_feed", fake_download)

    first = await client.post(
        "/api/v1/research-ingestion/run",
        json={"source_ids": [source_id], "max_items_per_source": 10},
    )
    assert first.status_code == 200
    assert first.json()["created"] == 1
    assert first.json()["duplicates"] == 0
    assert first.json()["results"][0]["status"] == "success"

    second = await client.post(
        "/api/v1/research-ingestion/run",
        json={"source_ids": [source_id], "max_items_per_source": 10},
    )
    assert second.status_code == 200
    assert second.json()["created"] == 0
    assert second.json()["duplicates"] == 1


async def test_rss_ingestion_reports_source_failure_without_crashing(
    client: AsyncClient,
    monkeypatch,
) -> None:
    source_id = await _create_rss_source(client)

    async def fake_download(url: str) -> bytes:
        raise ValueError("Feed URL is invalid.")

    monkeypatch.setattr(research_ingestion, "_download_feed", fake_download)
    response = await client.post(
        "/api/v1/research-ingestion/run",
        json={"source_ids": [source_id]},
    )

    assert response.status_code == 200
    assert response.json()["failed_sources"] == 1
    assert response.json()["results"][0]["errors"] == ["Feed URL is invalid."]


async def test_rss_ingestion_requires_admin(client: AsyncClient) -> None:
    # The fixture authenticates as an administrator; this test confirms the
    # endpoint rejects an unauthenticated request independently.
    response = await client.post(
        "/api/v1/research-ingestion/run",
        json={},
        headers={"Authorization": ""},
    )
    assert response.status_code == 401


def test_local_feed_urls_are_rejected() -> None:
    import pytest

    from app.services.research_ingestion import _validate_feed_url

    with pytest.raises(ValueError):
        _validate_feed_url("http://localhost:8000/internal")
