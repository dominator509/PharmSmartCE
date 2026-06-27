# SPEC-001 — Core Domain

**Status:** Accepted
**Owner:** founding-eng
**Date:** 2026-01
**Linked Roadmap Phase:** P1
**Linked ExecPlans:** EP-002

## User-Visible Goal
Domain layer encodes the rules of CE generation so that no infrastructure
mistake can produce an ungrounded or untraceable question.

## Non-Goals
- Persistence (SPEC-002).
- HTTP shapes (SPEC-003).
- UI (SPEC-004).

## Required Behaviors
- `Question` constructor raises `DomainError` if `source_doc_id`,
  `source_page`, or `source_span` is empty.
- `GroundedLLM.generate_question(chunk)` returns the
  `<<<INSUFFICIENT_CONTEXT>>>` marker if context is insufficient; service
  discards and retries.
- `CitationValidator.validate(question, chunk)` returns `True` iff
  token-overlap between question rationale and chunk text ≥
  `CITATION_MIN_OVERLAP_RATIO`.
- `RAGRetriever.retrieve(course, n, seed)` is deterministic for a given
  seed; produces `n` distinct chunks.
- Session is created only when ≥ `n_required` validated Questions exist.

## Inputs / Outputs
- `Course`, `Chunk` → `Question` (via `GroundedLLM`).
- `Question, Chunk` → `bool` (via `CitationValidator`).
- `Course, seed` → `list[Chunk]` (via `RAGRetriever`).

## Error States
- `DomainError` (invariant violated).
- `GroundingError` (validator rejected all retries for a slot).
- `InsufficientContextError` (LLM refused).

## Data Rules
No I/O in domain. Pure Python. No SQLAlchemy. No `httpx`.

## Security Rules
No raw chunk text in error messages (could leak source content).

## Performance Rules
Domain operations must be O(N) over input size.

## Observability Rules
Domain raises typed exceptions; observability added at service layer.

## Required Tests
- Unit: `test_question_invariants.py`, `test_grounded_llm.py`,
  `test_citation_validator.py`, `test_rag_retriever.py`.
- Each invariant has one passing + one failing test case.

## Acceptance Criteria
- [ ] All domain unit tests pass.
- [ ] `Question` rejects empty citation in test.
- [ ] `GroundedLLM` refuses outside context in test.
- [ ] `CitationValidator` rejects overlap < `CITATION_MIN_OVERLAP_RATIO`.
- [ ] `RAGRetriever` is deterministic for fixed seed in test.
