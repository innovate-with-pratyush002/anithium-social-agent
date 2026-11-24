from app.worker import create_scheduler


def test_research_scheduler_registers_bounded_non_overlapping_jobs() -> None:
    scheduler = create_scheduler()
    ingestion = scheduler.get_job("research-ingestion")
    analysis = scheduler.get_job("research-analysis")

    assert ingestion is not None
    assert analysis is not None
    assert ingestion.max_instances == 1
    assert analysis.max_instances == 1
    assert ingestion.coalesce is True
    assert analysis.coalesce is True
    assert ingestion.next_run_time is not None
    assert analysis.next_run_time is not None
