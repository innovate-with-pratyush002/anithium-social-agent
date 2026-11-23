from app import models  # noqa: F401 — import models to populate metadata.
from app.db.base import Base


def test_domain_models_register_expected_tables() -> None:
    expected = {
        "users",
        "sources",
        "research_items",
        "content_drafts",
        "approvals",
        "publishing_records",
    }

    assert expected.issubset(Base.metadata.tables.keys())


def test_approval_is_one_to_one_with_content_draft() -> None:
    approval_table = Base.metadata.tables["approvals"]
    draft_id = approval_table.c.content_draft_id

    assert draft_id.unique is True
    assert draft_id.nullable is False


def test_content_draft_platform_is_constrained() -> None:
    constraints = Base.metadata.tables["content_drafts"].constraints
    check_sql = {
        str(constraint.sqltext)
        for constraint in constraints
        if hasattr(constraint, "sqltext")
    }

    assert any(
        "linkedin" in expression and "instagram" in expression and "'x'" in expression
        for expression in check_sql
    )
