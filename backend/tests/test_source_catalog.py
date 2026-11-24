from app.scripts.seed_research_sources import SOURCE_CATALOG


def test_research_source_catalog_has_unique_http_feed_urls() -> None:
    urls = [source.url for source in SOURCE_CATALOG]

    assert len(urls) == len(set(urls))
    assert len(SOURCE_CATALOG) >= 5
    assert all(url.startswith("https://") for url in urls)


def test_research_source_catalog_has_valid_reliability_and_metadata() -> None:
    for source in SOURCE_CATALOG:
        assert 0 <= source.reliability_score <= 1
        assert source.name.strip()
        assert source.description.strip()
        assert source.config["topics"]
        assert source.config["source_kind"] in {
            "official",
            "research_repository",
        }
