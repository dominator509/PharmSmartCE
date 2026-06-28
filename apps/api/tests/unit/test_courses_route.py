from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.api.routes.courses import CourseCreateDTO


def test_course_create_dto_accepts_valid_numeric_fields() -> None:
    dto = CourseCreateDTO(title="Cardiology CE", n_questions=6, pass_pct=70)

    assert dto.n_questions == 6
    assert dto.pass_pct == 70


@pytest.mark.parametrize(
    "field_name, value",
    [
        ("n_questions", True),
        ("pass_pct", False),
    ],
)
def test_course_create_dto_rejects_boolean_numeric_fields(field_name: str, value: bool) -> None:
    kwargs = {"title": "Cardiology CE", "n_questions": 6, "pass_pct": 70}
    kwargs[field_name] = value

    with pytest.raises(ValidationError):
        CourseCreateDTO(**kwargs)
