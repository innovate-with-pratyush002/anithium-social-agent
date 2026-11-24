import json

import pytest
from pydantic import ValidationError

from app.services.research_intelligence import parse_research_analysis


def _analysis_payload(key_points: list[object]) -> str:
    return json.dumps(
        {
            "summary": "This summary is based only on the supplied source material.",
            "topic": "Artificial Intelligence",
            "language": "en",
            "relevance_score": 0.9,
            "key_points": key_points,
        }
    )


def test_parser_trims_excess_key_points_and_removes_duplicates() -> None:
    content = _analysis_payload(
        [
            "  First supported point  ",
            "Second supported point",
            "first supported point",
            "",
            "Third supported point",
            "Fourth supported point",
            "Fifth supported point",
            "Sixth supported point",
        ]
    )

    result = parse_research_analysis(content)

    assert result.key_points == [
        "First supported point",
        "Second supported point",
        "Third supported point",
        "Fourth supported point",
        "Fifth supported point",
    ]


def test_parser_rejects_non_string_key_points() -> None:
    content = _analysis_payload(["Valid point", 42])

    with pytest.raises(ValidationError):
        parse_research_analysis(content)


def test_parser_rejects_invalid_json() -> None:
    with pytest.raises(ValueError, match="invalid JSON"):
        parse_research_analysis("{not-json}")


def test_parser_rejects_non_object_json() -> None:
    with pytest.raises(ValueError, match="JSON object"):
        parse_research_analysis("[]")
