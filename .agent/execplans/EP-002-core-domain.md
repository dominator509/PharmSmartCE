# EP-002 — Core Domain + LLM/RAG Plumbing

**Phase:** P1

## 1. Purpose / Big Picture
Implement the pure domain layer plus the grounded-generation core: domain entities, `GroundedLLM`, `RAGRetriever`, `CitationValidator`, and a deterministic `FakeLLM` adapter. No database, no HTTP. This layer guarantees the clinical accuracy invariants from `SPEC-001`.

## 2. Scope
- Domain entities in `apps/api/app/domain/`
- Adapter Protocols in `apps/api/app/services/ports/`
- `FakeLLM` adapter (deterministic by `sha256(prompt)`)
- `GroundedLLM` wrapper with locked system prompt and chunk delimiters
- `CitationValidator` (token-overlap ratio)
- `RAGRetriever` stub (in-memory, deterministic by seed)
- Unit tests for all invariants

## 3. Non-goals
- Database persistence (EP-003)
- HTTP routes (EP-004)
- Real `llama-cpp-python` adapter wiring (deferred to EP-008/EP-009 model download)
- OpenAI adapter implementation (deferred to EP-006/EP-008)

## 4. Context and Orientation
Builds on EP-001 skeleton. Implements `SPEC-001`. All code is pure Python with no I/O. Tests use `FakeLLM` exclusively.

## 5. Files to Read First
- `AGENTS.md`
- `ARCHITECTURE.md`
- `.agent/specs/SPEC-001-core-domain.md`
- `apps/api/pyproject.toml`

## 6. Files to Change
- `apps/api/app/domain/entities.py`
- `apps/api/app/domain/errors.py`
- `apps/api/app/services/ports/__init__.py`
- `apps/api/app/services/ports/llm.py`
- `apps/api/app/services/ports/embeddings.py`
- `apps/api/app/adapters/llm/__init__.py`
- `apps/api/app/adapters/llm/fake_adapter.py`
- `apps/api/app/services/generation/__init__.py`
- `apps/api/app/services/generation/grounded_llm.py`
- `apps/api/app/services/generation/citation_validator.py`
- `apps/api/app/services/generation/rag_retriever.py`
- `apps/api/tests/unit/domain/test_question_invariants.py`
- `apps/api/tests/unit/services/test_grounded_llm.py`
- `apps/api/tests/unit/services/test_citation_validator.py`
- `apps/api/tests/unit/services/test_rag_retriever.py`

## 7. Interfaces and Contracts
`LLMPort.generate(prompt, max_tokens) -> str` (Protocol). `GroundedLLM.generate_question(chunk: Chunk) -> Question | raises InsufficientContextError`. `CitationValidator.validate(question: Question, chunk: Chunk) -> bool`. `RAGRetriever.retrieve(course: Course, n: int, seed: str) -> list[Chunk]`. No types here touch SQLAlchemy or HTTP.

## 8. Milestones

### M1: Domain entities + errors
- **Files to read:** `.agent/specs/SPEC-001-core-domain.md`
- **Files to change:** `apps/api/app/domain/entities.py`, `apps/api/app/domain/errors.py`
- **Exact edits expected:** Define Pydantic models or frozen dataclasses for User, Org, Course, Source, Chunk, Question, Session, Answer, CERecord. `Question.__post_init__` raises `DomainError` if any of `source_doc_id` / `source_page` / `source_span` is empty. Define `DomainError`, `GroundingError`, `InsufficientContextError` in errors.py.
- **Validation command:** `uv run --directory apps/api pytest tests/unit/domain -q`
- **Expected result:** All domain tests pass.
- **Recovery:** If imports fail, ensure `apps/api/app/__init__.py` exists and `domain/__init__.py` exports the entities.

### M2: Define LLMPort and EmbeddingPort Protocols
- **Files to read:** `ARCHITECTURE.md`
- **Files to change:** `apps/api/app/services/ports/__init__.py`, `apps/api/app/services/ports/llm.py`, `apps/api/app/services/ports/embeddings.py`
- **Exact edits expected:** `llm.py` defines `class LLMPort(Protocol): def generate(self, prompt: str, max_tokens: int) -> str: ...`. `embeddings.py` defines `class EmbeddingPort(Protocol): def embed(self, texts: list[str]) -> list[list[float]]: ...`.
- **Validation command:** `uv run --directory apps/api ruff check app/services/ports`
- **Expected result:** ruff: no issues.
- **Recovery:** If `Protocol` import errors, use `from typing import Protocol`.

### M3: Implement FakeLLM adapter (deterministic)
- **Files to read:** `.agent/specs/SPEC-001-core-domain.md`
- **Files to change:** `apps/api/app/adapters/llm/__init__.py`, `apps/api/app/adapters/llm/fake_adapter.py`
- **Exact edits expected:** FakeLLM hashes the prompt with sha256 and returns a canned JSON-like string. If the prompt does NOT contain `<<<context_start>>>...<<<context_end>>>`, return the literal `<<<INSUFFICIENT_CONTEXT>>>`. Otherwise echo a short MCQ derived from the chunk text.
- **Validation command:** `uv run --directory apps/api pytest tests/unit/services/test_grounded_llm.py::test_fake_llm_deterministic -q`
- **Expected result:** Test passes.
- **Recovery:** If output non-deterministic, ensure no time.time/randomness; only use sha256(prompt).

### M4: Implement GroundedLLM wrapper
- **Files to read:** `.agent/specs/SPEC-001-core-domain.md`, `SECURITY.md`
- **Files to change:** `apps/api/app/services/generation/__init__.py`, `apps/api/app/services/generation/grounded_llm.py`
- **Exact edits expected:** System prompt is a module-level constant. Build prompt: SYSTEM + chunk wrapped in `<<<context_start id="{doc_id}:{page}:{span}">>> {text} <<<context_end>>>` + instructions to refuse outside context. Call `LLMPort.generate(...)`. Parse output; if `<<<INSUFFICIENT_CONTEXT>>>` raise `InsufficientContextError`. Build and return a `Question` with citation fields from the chunk.
- **Validation command:** `uv run --directory apps/api pytest tests/unit/services/test_grounded_llm.py -q`
- **Expected result:** All tests pass — including refusal and citation-population.
- **Recovery:** If parsing fragile, make FakeLLM output match expected parser; do not loosen parser.

### M5: Implement CitationValidator
- **Files to read:** `.agent/specs/SPEC-001-core-domain.md`
- **Files to change:** `apps/api/app/services/generation/citation_validator.py`
- **Exact edits expected:** Tokenize question.rationale and chunk.text on whitespace + lowercase + remove punctuation. Compute overlap = |intersect| / |question_rationale_tokens|. Return overlap >= settings.CITATION_MIN_OVERLAP_RATIO. Expose `compute_overlap(...)` for tests.
- **Validation command:** `uv run --directory apps/api pytest tests/unit/services/test_citation_validator.py -q`
- **Expected result:** Tests pass (high-overlap accepted; low-overlap rejected).
- **Recovery:** If tokenizer too aggressive, use regex `\w+` and document.

### M6: Implement RAGRetriever stub
- **Files to read:** `.agent/specs/SPEC-001-core-domain.md`
- **Files to change:** `apps/api/app/services/generation/rag_retriever.py`
- **Exact edits expected:** Constructor takes a callable `chunk_source` returning list[Chunk]. `retrieve(course, n, seed)`: seed-shuffle (random.Random(seed)) the chunk list, return first n distinct chunks. No embedding I/O yet (deferred to EP-003 via EmbeddingPort).
- **Validation command:** `uv run --directory apps/api pytest tests/unit/services/test_rag_retriever.py -q`
- **Expected result:** Determinism test passes (same seed → same chunks).
- **Recovery:** If determinism fails, ensure `random.Random(seed)` not `random.shuffle` (global RNG).

### M7: Run full unit suite
- **Files to read:** (none new)
- **Files to change:** (none)
- **Exact edits expected:** No edits; gate.
- **Validation command:** `uv run --directory apps/api pytest tests/unit -q --cov=app --cov-report=term`
- **Expected result:** All unit tests pass; coverage on `app/domain` and `app/services/generation` ≥ 95%.
- **Recovery:** If a sub-test fails, switch to debug-validation-failure procedure.

## 9. Concrete Steps
Execute milestones in order. After each: run validation, verify expected,
tick `Progress`, append one-line note. Apply bounded-retry (AGENTS §7) on
any failure. Continue autonomously. Stop only under STOP conditions.

## 10. Validation and Acceptance
- All milestone validations pass.
- `scripts/verify.sh` exit 0.
- Acceptance criteria:
  - [ ] `Question` rejects empty citation in test
  - [ ] `GroundedLLM` returns `InsufficientContextError` when chunk delimiters absent
  - [ ] `CitationValidator.validate` rejects overlap below `CITATION_MIN_OVERLAP_RATIO`
  - [ ] `RAGRetriever.retrieve` is deterministic for a fixed seed
  - [ ] Unit coverage on the affected modules ≥ 95%

## 11. Idempotence and Recovery
Re-running is safe: deterministic tests; no I/O. Re-running a milestone produces the same files (overwrite-by-edit).

## 12. Progress
- [ ] M1: Domain entities + errors
- [ ] M2: Define LLMPort and EmbeddingPort Protocols
- [ ] M3: Implement FakeLLM adapter (deterministic)
- [ ] M4: Implement GroundedLLM wrapper
- [ ] M5: Implement CitationValidator
- [ ] M6: Implement RAGRetriever stub
- [ ] M7: Run full unit suite

## 13. Surprises & Discoveries
(empty — append entries here as they occur)

## 14. Decision Log
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
(to be filled at completion)
