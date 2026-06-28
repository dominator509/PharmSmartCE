import pytest

from app.domain.entities import Course
from app.domain.errors import DomainError


def test_course_accepts_valid_fields() -> None:
    course = Course(id="course-1", org_id="org-1", title="Cardiology CE")

    assert course.org_id == "org-1"
    assert course.title == "Cardiology CE"


@pytest.mark.parametrize(
    "field_name",
    ["org_id", "title"],
)
def test_course_rejects_blank_required_text(field_name: str) -> None:
    kwargs = {"id": "course-1", "org_id": "org-1", "title": "Cardiology CE"}
    kwargs[field_name] = "   "

    with pytest.raises(DomainError):
        Course(**kwargs)
