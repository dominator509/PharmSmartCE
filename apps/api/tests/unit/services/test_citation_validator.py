from app.domain.entities import Chunk, Question
from app.services.generation.citation_validator import (
    CITATION_MIN_OVERLAP_RATIO,
    CitationValidator,
    compute_overlap,
)


def test_compute_overlap_uses_token_intersection() -> None:
    ratio = compute_overlap(
        "Beta blockers reduce heart rate and blood pressure.",
        "Beta blockers reduce heart rate and improve outcomes.",
    )

    assert ratio > 0.5


def test_compute_overlap_returns_zero_for_empty_rationale() -> None:
    assert compute_overlap("", "Beta blockers reduce heart rate.") == 0.0


def test_citation_validator_accepts_high_overlap_and_rejects_low_overlap() -> None:
    validator = CitationValidator()
    chunk = Chunk(
        doc_id="doc-1",
        page=4,
        span="p4:s2",
        text="Beta blockers reduce heart rate and blood pressure.",
    )
    good_question = Question(
        stem="Which statement fits the source?",
        choices=("A", "B", "C", "D"),
        correct_choice_index=0,
        rationale="Beta blockers reduce heart rate and blood pressure.",
        source_doc_id="doc-1",
        source_page=4,
        source_span="p4:s2",
    )
    bad_question = Question(
        stem="Which statement fits the source?",
        choices=("A", "B", "C", "D"),
        correct_choice_index=0,
        rationale="This rationale uses unrelated wording.",
        source_doc_id="doc-1",
        source_page=4,
        source_span="p4:s2",
    )

    assert validator.validate(good_question, chunk) is True
    assert validator.validate(bad_question, chunk) is False
    assert CITATION_MIN_OVERLAP_RATIO == 0.4
