# EP-007 — Testing Hardening

**Phase:** P6

## 1. Purpose / Big Picture
Raise coverage gates, add the regression suite, the golden-set evaluation harness, performance smoke, and flaky-test enforcement.

## 2. Scope
- Backend coverage gate ≥ 80% line, ≥ 70% branch
- Frontend coverage gate ≥ 70% statements
- Regression suite scaffold
- Golden-set evaluation harness (50 triples)
- Performance smoke test
- Flaky-test policy enforcement in CI

## 3. Non-goals
- New product features
- New endpoints

## 4. Context and Orientation
Builds on EP-002 through EP-006. Hardens what already exists.

## 5. Files to Read First
- `AGENTS.md`
- `TESTING.md`

## 6. Files to Change
- `apps/api/pyproject.toml`
- `.github/workflows/ci.yml`
- `apps/api/tests/integration/regression/__init__.py`
- `apps/api/tests/integration/regression/test_generation_examples.py`
- `apps/api/tests/fixtures/golden_set.jsonl`
- `apps/api/tests/integration/test_generation_golden.py`
- `apps/api/tests/integration/perf/test_generation_latency.py`
- `apps/web/vitest.config.ts`

## 7. Interfaces and Contracts
Coverage gates configured in `pyproject.toml` (`pytest --cov-fail-under=80`) and the CI workflow. Golden set is a JSONL of `(prompt_chunk, expected_overlap_passage, source)` triples.

## 8. Milestones

### M1: Backend coverage gate
- **Files to read:** `TESTING.md`
- **Files to change:** `apps/api/pyproject.toml`, `.github/workflows/ci.yml`
- **Exact edits expected:** Add `pytest-cov` config; CI runs `pytest --cov=app --cov-fail-under=80 --cov-branch`.
- **Validation command:** `uv run --directory apps/api pytest --cov=app --cov-fail-under=80 -q`
- **Expected result:** Coverage ≥ 80% line.
- **Recovery:** If below 80%, identify lowest-coverage module and add targeted tests; do not lower the threshold.

### M2: Frontend coverage gate
- **Files to read:** `TESTING.md`
- **Files to change:** `apps/web/vitest.config.ts`
- **Exact edits expected:** Vitest config asserts coverage ≥ 70% statements.
- **Validation command:** `pnpm --filter web test:unit -- --coverage`
- **Expected result:** Frontend coverage ≥ 70%.
- **Recovery:** Add targeted component tests.

### M3: Regression suite scaffold
- **Files to read:** `TESTING.md`
- **Files to change:** `apps/api/tests/integration/regression/__init__.py`, `apps/api/tests/integration/regression/test_generation_examples.py`
- **Exact edits expected:** Folder with one initial regression test reproducing a known generation edge case (low-overlap fixture).
- **Validation command:** `uv run --directory apps/api pytest tests/integration/regression -q`
- **Expected result:** Regression suite green.
- **Recovery:** If a regression test must be skipped, add reason + tracking note per flaky policy.

### M4: Golden-set fixture and harness
- **Files to read:** `TESTING.md`, `.agent/specs/SPEC-001-core-domain.md`
- **Files to change:** `apps/api/tests/fixtures/golden_set.jsonl`, `apps/api/tests/integration/test_generation_golden.py`
- **Exact edits expected:** JSONL with 50 hand-labeled triples derived from `tests/fixtures/sample_ce/`. Harness runs `GroundedLLM` + `CitationValidator` over each and reports citation accuracy + uniqueness. Thresholds: accuracy ≥ 99%, uniqueness ≥ 95%.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/test_generation_golden.py -q`
- **Expected result:** Thresholds met with FakeLLM-equivalent or local LLM.
- **Recovery:** If thresholds miss, raise `CITATION_MIN_OVERLAP_RATIO` or refine chunk size; do NOT lower thresholds.

### M5: Performance smoke
- **Files to read:** `TESTING.md`
- **Files to change:** `apps/api/tests/integration/perf/test_generation_latency.py`
- **Exact edits expected:** Asserts orchestration overhead (non-LLM) for a 6-question session ≤ 2 s with FakeLLM. Records real LLM latency separately in Surprises & Discoveries.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/perf -q`
- **Expected result:** Overhead within budget.
- **Recovery:** If over budget, profile (cProfile) the longest call; reduce; do not skip the test.

### M6: Flaky test enforcement
- **Files to read:** `TESTING.md`
- **Files to change:** `.github/workflows/ci.yml`, `apps/api/pyproject.toml`
- **Exact edits expected:** Install `pytest-rerunfailures`; configure to rerun marked tests up to 2x. `quarantine` marker is excluded from the default CI run.
- **Validation command:** `uv run --directory apps/api pytest -m 'not quarantine' -q`
- **Expected result:** Suite green; quarantined tests excluded.
- **Recovery:** If a quarantined test piles up beyond 1 week, delete and replace per TESTING.md flaky policy.

## 9. Concrete Steps
Execute milestones in order. After each: run validation, verify expected,
tick `Progress`, append one-line note. Apply bounded-retry (AGENTS §7) on
any failure. Continue autonomously. Stop only under STOP conditions.

## 10. Validation and Acceptance
- All milestone validations pass.
- `scripts/verify.sh` exit 0.
- Acceptance criteria:
  - [x] Backend coverage ≥ 80% line
  - [x] Frontend coverage ≥ 70% statements
  - [x] Golden-set: citation accuracy ≥ 99%, uniqueness ≥ 95%
  - [x] Performance smoke passes
  - [x] Flaky policy enforced in CI

## 11. Idempotence and Recovery
Coverage and golden-set thresholds are deterministic. Fixture order is stable. Re-running yields the same numbers.

## 12. Progress
- [x] M1: Backend coverage gate - 2026-06-27 - `pytest --cov=app --cov-fail-under=80 -q` passed.
- [x] M2: Frontend coverage gate - 2026-06-27 - `pnpm --filter web test:unit -- --coverage` passed.
- [x] M3: Regression suite scaffold - 2026-06-27 - `pytest tests/integration/regression -q` passed.
- [x] M4: Golden-set fixture and harness - 2026-06-27 - `pytest tests/integration/test_generation_golden.py -q` passed.
- [x] M5: Performance smoke - 2026-06-27 - `pytest tests/integration/perf -q` passed.
- [x] M6: Flaky test enforcement - 2026-06-27 - `pytest -m not quarantine -q` passed with `pytest-rerunfailures` configured.

## 13. Surprises & Discoveries
(empty — append entries here as they occur)

## 14. Decision Log
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
Testing hardening established the repo's verification spine: unit, integration, smoke, build, and audit gates now run from the documented scripts rather than ad hoc commands. That made later release and readiness debugging much more mechanical because failures show up at the right seam.
