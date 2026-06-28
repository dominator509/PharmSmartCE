from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.errors import DomainError


@dataclass(frozen=True, slots=True)
class Org:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class User:
    id: str
    org_id: str
    email: str
    display_name: str = ""


@dataclass(frozen=True, slots=True)
class Course:
    id: str
    org_id: str
    title: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class Source:
    id: str
    course_id: str
    doc_id: str
    filename: str
    page_count: int = 0


@dataclass(frozen=True, slots=True)
class Chunk:
    doc_id: str
    page: int
    span: str
    text: str
    course_id: str = ""


@dataclass(frozen=True, slots=True)
class Question:
    stem: str
    choices: tuple[str, ...]
    correct_choice_index: int
    rationale: str
    source_doc_id: str
    source_page: int | None
    source_span: str
    id: str = ""

    def __post_init__(self) -> None:
        if not self.stem.strip():
            raise DomainError("Question requires a stem.")
        if not self.rationale.strip():
            raise DomainError("Question requires a rationale.")
        if not self.source_doc_id.strip():
            raise DomainError("Question requires a source_doc_id.")
        if self.source_page is None or self.source_page <= 0:
            raise DomainError("Question requires a positive source_page.")
        if not self.source_span.strip():
            raise DomainError("Question requires a source_span.")
        if not self.choices:
            raise DomainError("Question requires at least one answer choice.")
        if not 0 <= self.correct_choice_index < len(self.choices):
            raise DomainError("Question correct_choice_index out of range.")


@dataclass(frozen=True, slots=True)
class Session:
    id: str
    user_id: str
    course_id: str
    question_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class Answer:
    id: str
    session_id: str
    question_id: str
    selected_choice_index: int
    is_correct: bool


@dataclass(frozen=True, slots=True)
class CERecord:
    id: str
    session_id: str
    user_id: str
    course_id: str
    passed: bool
    score_percent: float
