from __future__ import annotations

import pytest

from app.api.routes.sessions import _question_choices


def test_question_choices_extracts_valid_string_choices() -> None:
    assert _question_choices({"choices": ["A", "B", "C"]}) == ["A", "B", "C"]


@pytest.mark.parametrize(
    "options",
    [
        {},
        {"choices": []},
        {"choices": ["A", 1]},
        {"choices": "A"},
    ],
)
def test_question_choices_rejects_invalid_options(options: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        _question_choices(options)
