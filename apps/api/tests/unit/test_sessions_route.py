from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.api.routes.sessions import AnswerDTO, _question_choices


def test_question_choices_extracts_valid_string_choices() -> None:
    assert _question_choices({"choices": ["A", "B", "C"]}) == ["A", "B", "C"]


def test_answer_dto_rejects_boolean_choice_index() -> None:
    with pytest.raises(ValidationError):
        AnswerDTO(question_id="question-1", chosen_index=True)


def test_answer_dto_rejects_blank_question_id() -> None:
    with pytest.raises(ValidationError):
        AnswerDTO(question_id="   ", chosen_index=1)


def test_answer_dto_rejects_overlong_question_id() -> None:
    with pytest.raises(ValidationError):
        AnswerDTO(question_id="q" * 37, chosen_index=1)


def test_answer_dto_rejects_negative_choice_index() -> None:
    with pytest.raises(ValidationError):
        AnswerDTO(question_id="question-1", chosen_index=-1)


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
