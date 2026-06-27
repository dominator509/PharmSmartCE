import pytest

from app.domain.entities import Question
from app.domain.errors import DomainError


def test_question_accepts_valid_citation_fields() -> None:
    question = Question(
        stem="What is the key point?",
        choices=("A", "B", "C", "D"),
        correct_choice_index=1,
        rationale="The source text explains the key point clearly.",
        source_doc_id="doc-1",
        source_page=7,
        source_span="p7:s1",
    )

    assert question.source_doc_id == "doc-1"
    assert question.source_page == 7
    assert question.source_span == "p7:s1"


@pytest.mark.parametrize(
    ("source_doc_id", "source_page", "source_span"),
    [
        ("", 7, "p7:s1"),
        ("doc-1", None, "p7:s1"),
        ("doc-1", 7, ""),
    ],
)
def test_question_rejects_empty_citation_fields(
    source_doc_id: str,
    source_page: int | None,
    source_span: str,
) -> None:
    with pytest.raises(DomainError):
        Question(
            stem="What is the key point?",
            choices=("A", "B", "C", "D"),
            correct_choice_index=1,
            rationale="The source text explains the key point clearly.",
            source_doc_id=source_doc_id,
            source_page=source_page,
            source_span=source_span,
        )
