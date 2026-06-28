from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.errors import DomainError


@dataclass(frozen=True, slots=True)
class Org:
    id: str
    name: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise DomainError("Org requires an id.")
        if not self.name.strip():
            raise DomainError("Org requires a name.")


@dataclass(frozen=True, slots=True)
class User:
    id: str
    org_id: str
    email: str
    display_name: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise DomainError("User requires an id.")
        if not self.org_id.strip():
            raise DomainError("User requires an org_id.")
        if not self.email.strip():
            raise DomainError("User requires an email.")


@dataclass(frozen=True, slots=True)
class Course:
    id: str
    org_id: str
    title: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.org_id.strip():
            raise DomainError("Course requires an org_id.")
        if not self.title.strip():
            raise DomainError("Course requires a title.")


@dataclass(frozen=True, slots=True)
class Source:
    id: str
    course_id: str
    doc_id: str
    filename: str
    page_count: int = 0

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise DomainError("Source requires an id.")
        if not self.course_id.strip():
            raise DomainError("Source requires a course_id.")
        if not self.doc_id.strip():
            raise DomainError("Source requires a doc_id.")
        if not self.filename.strip():
            raise DomainError("Source requires a filename.")
        if self.page_count < 0:
            raise DomainError("Source requires a non-negative page_count.")


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

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise DomainError("Session requires an id.")
        if not self.user_id.strip():
            raise DomainError("Session requires a user_id.")
        if not self.course_id.strip():
            raise DomainError("Session requires a course_id.")


@dataclass(frozen=True, slots=True)
class Answer:
    id: str
    session_id: str
    question_id: str
    selected_choice_index: int
    is_correct: bool

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise DomainError("Answer requires an id.")
        if not self.session_id.strip():
            raise DomainError("Answer requires a session_id.")
        if not self.question_id.strip():
            raise DomainError("Answer requires a question_id.")
        if self.selected_choice_index < 0:
            raise DomainError("Answer requires a non-negative selected_choice_index.")


@dataclass(frozen=True, slots=True)
class CERecord:
    id: str
    session_id: str
    user_id: str
    course_id: str
    passed: bool
    score_percent: float

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise DomainError("CERecord requires an id.")
        if not self.session_id.strip():
            raise DomainError("CERecord requires a session_id.")
        if not self.user_id.strip():
            raise DomainError("CERecord requires a user_id.")
        if not self.course_id.strip():
            raise DomainError("CERecord requires a course_id.")
        if not 0 <= self.score_percent <= 100:
            raise DomainError("CERecord requires a score_percent between 0 and 100.")
