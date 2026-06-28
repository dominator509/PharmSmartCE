import pytest

from app.domain.entities import Session
from app.domain.errors import DomainError


def test_session_accepts_unique_question_ids() -> None:
    session = Session(
        id="session-1",
        user_id="user-1",
        course_id="course-1",
        question_ids=("question-1", "question-2"),
    )

    assert session.question_ids == ("question-1", "question-2")


@pytest.mark.parametrize(
    "question_ids",
    [
        ("question-1", ""),
        ("question-1", "question-1"),
    ],
)
def test_session_rejects_blank_or_duplicate_question_ids(question_ids: tuple[str, ...]) -> None:
    with pytest.raises(DomainError):
        Session(
            id="session-1",
            user_id="user-1",
            course_id="course-1",
            question_ids=question_ids,
        )
