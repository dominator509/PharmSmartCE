import pytest

from app.domain.entities import Answer, CERecord, Org, Session, Source, User
from app.domain.errors import DomainError


@pytest.mark.parametrize(
    "entity_type, kwargs, field_name",
    [
        (Org, {"id": "org-1", "name": "Metro CE"}, "name"),
        (User, {"id": "user-1", "org_id": "org-1", "email": "user@example.com"}, "email"),
        (
            Source,
            {
                "id": "source-1",
                "course_id": "course-1",
                "doc_id": "doc-1",
                "filename": "source.pdf",
            },
            "filename",
        ),
        (Session, {"id": "session-1", "user_id": "user-1", "course_id": "course-1"}, "course_id"),
        (
            Answer,
            {
                "id": "answer-1",
                "session_id": "session-1",
                "question_id": "question-1",
                "selected_choice_index": 0,
                "is_correct": True,
            },
            "question_id",
        ),
        (
            CERecord,
            {
                "id": "record-1",
                "session_id": "session-1",
                "user_id": "user-1",
                "course_id": "course-1",
                "passed": True,
                "score_percent": 100.0,
            },
            "score_percent",
        ),
    ],
)
def test_domain_records_accept_valid_baseline_values(entity_type, kwargs, field_name) -> None:
    entity = entity_type(**kwargs)

    assert getattr(entity, field_name) == kwargs[field_name]


@pytest.mark.parametrize(
    "entity_type, kwargs, field_name, value",
    [
        (Org, {"id": "org-1", "name": "Metro CE"}, "name", "   "),
        (User, {"id": "user-1", "org_id": "org-1", "email": "user@example.com"}, "email", "   "),
        (
            Source,
            {
                "id": "source-1",
                "course_id": "course-1",
                "doc_id": "doc-1",
                "filename": "source.pdf",
            },
            "page_count",
            -1,
        ),
        (Session, {"id": "session-1", "user_id": "user-1", "course_id": "course-1"}, "id", "   "),
        (
            Answer,
            {
                "id": "answer-1",
                "session_id": "session-1",
                "question_id": "question-1",
                "selected_choice_index": 0,
                "is_correct": True,
            },
            "selected_choice_index",
            -1,
        ),
        (
            CERecord,
            {
                "id": "record-1",
                "session_id": "session-1",
                "user_id": "user-1",
                "course_id": "course-1",
                "passed": True,
                "score_percent": 100.0,
            },
            "score_percent",
            101.0,
        ),
    ],
)
def test_domain_records_reject_invalid_values(entity_type, kwargs, field_name, value) -> None:
    kwargs[field_name] = value

    with pytest.raises(DomainError):
        entity_type(**kwargs)
