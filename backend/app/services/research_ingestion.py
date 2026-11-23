import asyncio
import hashlib
import logging
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

import feedparser
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.research_item import ResearchItem
from app.models.source import Source
from app.schemas.research_ingestion import (
    ResearchIngestionRequest,
    ResearchIngestionResponse,
    SourceIngestionResult,
)

logger = logging.getLogger(__name__)
MAX_FEED_BYTES = 2 * 1024 * 1024
REQUEST_TIMEOUT_SECONDS = 20


def _plain_text(value: str | None) -> str | None:
    if not value:
        return None
    text = re.sub(r"<[^>]*>", " ", value)
    text = unescape(re.sub(r"\s+", " ", text)).strip()
    return text or None


def _published_at(entry: Any) -> datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        try:
            import calendar

            return datetime.fromtimestamp(calendar.timegm(parsed), tz=UTC)
        except (OverflowError, TypeError, ValueError):
            return None

    raw = entry.get("published") or entry.get("updated")
    if raw:
        try:
            value = parsedate_to_datetime(raw)
            return value.replace(tzinfo=UTC) if value.tzinfo is None else value
        except (TypeError, ValueError, OverflowError):
            return None
    return None


def _entry_hash(url: str | None, title: str, published_at: datetime | None) -> str:
    identity = url or f"{title.strip().casefold()}|{published_at.isoformat() if published_at else ''}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def _validate_feed_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("RSS source URL must use HTTP or HTTPS.")
    hostname = parsed.hostname.casefold()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".local"):
        raise ValueError("Local network RSS URLs are not allowed.")


async def _download_feed(url: str) -> bytes:
    _validate_feed_url(url)
    timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=False,
        trust_env=False,
        headers={"User-Agent": "AnithiumResearchBot/1.0 (+RSS ingestion)"},
    ) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" in content_type:
                raise ValueError("The URL returned HTML, not an RSS/Atom feed.")
            chunks: list[bytes] = []
            size = 0
            async for chunk in response.aiter_bytes():
                size += len(chunk)
                if size > MAX_FEED_BYTES:
                    raise ValueError("RSS feed exceeds the 2 MB size limit.")
                chunks.append(chunk)
            return b"".join(chunks)


async def ingest_research(
    session: AsyncSession,
    payload: ResearchIngestionRequest,
) -> ResearchIngestionResponse:
    started_at = datetime.now(UTC)
    query = select(Source).where(Source.is_active.is_(True), Source.source_type == "rss")
    if payload.source_ids:
        query = query.where(Source.id.in_(payload.source_ids))
    sources = list((await session.scalars(query.order_by(Source.name.asc()))).all())

    results: list[SourceIngestionResult] = []
    for source in sources:
        result = SourceIngestionResult(
            source_id=source.id,
            source_name=source.name,
            status="success",
        )
        try:
            raw_feed = await _download_feed(source.url)
            parsed_feed = await asyncio.to_thread(feedparser.parse, raw_feed)
            if parsed_feed.bozo and not parsed_feed.entries:
                raise ValueError("The feed could not be parsed as valid RSS/Atom.")
            entries = parsed_feed.entries[: payload.max_items_per_source]
            result.fetched = len(entries)

            for entry in entries:
                title = _plain_text(entry.get("title")) or "Untitled research item"
                link = entry.get("link")
                if link:
                    link = str(link).strip()
                    if urlparse(link).scheme not in {"http", "https"}:
                        link = None
                summary = _plain_text(entry.get("summary") or entry.get("description"))
                published_at = _published_at(entry)
                content_hash = _entry_hash(link, title, published_at)

                existing = await session.scalar(
                    select(ResearchItem.id).where(
                        (ResearchItem.url == link) if link else (
                            ResearchItem.content_hash == content_hash
                        )
                    )
                )
                if existing is not None:
                    result.duplicates += 1
                    continue

                tags = [
                    str(tag.get("term"))
                    for tag in entry.get("tags", [])
                    if tag.get("term")
                ]
                item = ResearchItem(
                    source_id=source.id,
                    title=title[:500],
                    url=link,
                    summary=summary,
                    content=None,
                    content_hash=content_hash,
                    topic=tags[0][:120] if tags else None,
                    language="en",
                    status="new",
                    published_at=published_at,
                    metadata_json={
                        "ingestion_method": "rss",
                        "feed_url": source.url,
                        "author": _plain_text(entry.get("author")),
                        "tags": tags[:20],
                    },
                )
                try:
                    async with session.begin_nested():
                        session.add(item)
                        await session.flush()
                    result.created += 1
                except Exception as exc:
                    logger.warning("Skipping RSS entry from source %s: %s", source.id, exc)
                    result.duplicates += 1

        except (httpx.HTTPError, ValueError, TimeoutError) as exc:
            result.status = "failed"
            result.errors.append(str(exc)[:500])
            logger.warning("RSS ingestion failed for source %s: %s", source.id, exc)
        except Exception as exc:
            result.status = "failed"
            result.errors.append("Unexpected ingestion error.")
            logger.exception("Unexpected RSS ingestion error for source %s", source.id)

        results.append(result)

    await session.commit()
    completed_at = datetime.now(UTC)
    return ResearchIngestionResponse(
        started_at=started_at,
        completed_at=completed_at,
        sources_processed=len(results),
        fetched=sum(item.fetched for item in results),
        created=sum(item.created for item in results),
        duplicates=sum(item.duplicates for item in results),
        failed_sources=sum(item.status == "failed" for item in results),
        results=results,
    )


__all__ = ["ingest_research"]
