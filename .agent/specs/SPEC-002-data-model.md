# SPEC-002 — Data Model

**Status:** Accepted
**Owner:** founding-eng
**Date:** 2026-01
**Linked Roadmap Phase:** P2
**Linked ExecPlans:** EP-003

## User-Visible Goal
Persist all entities required by SPEC-001 and SPEC-003 with constraints
that make ungrounded or untraceable data impossible at the DB level.

## Non-Goals
- Vector store schema (FAISS index files; not relational).
- Object storage layout (in `ARCHITECTURE.md`).

## Tables (summary)

| Table | Notable Columns |
|---|---|
| `orgs` | `id PK`, `name UNIQUE`, `created_at` |
| `users` | `id PK`, `org_id FK`, `email UNIQUE`, `password_hash`, `role` ∈ {admin,member}, `created_at` |
| `refresh_tokens` | `jti PK`, `user_id FK`, `token_sha256`, `expires_at`, `revoked_at`, `replaced_by_jti FK` |
| `courses` | `id PK`, `org_id FK`, `title`, `n_questions DEFAULT 6`, `pass_pct DEFAULT 70`, `status` ∈ {draft,ready}, `created_at` |
| `sources` | `id PK`, `course_id FK`, `filename`, `bytes`, `sha256`, `status` ∈ {uploaded,ingesting,ready,failed,quarantined}, `last_error`, `created_at` |
| `chunks` | `id PK`, `source_id FK`, `page INT NOT NULL`, `span_start INT NOT NULL`, `span_end INT NOT NULL`, `text TEXT NOT NULL`, `embedding_index BIGINT NOT NULL` |
| `sessions` | `id PK`, `course_id FK`, `user_id FK`, `seed`, `started_at`, `completed_at`, `score_pct`, `passed BOOL` |
| `questions` | `id PK`, `session_id FK`, `text`, `options JSONB`, `correct_index INT`, `rationale`, `source_doc_id FK NOT NULL`, `source_page INT NOT NULL`, `source_span TEXT NOT NULL`, `citation_overlap NUMERIC NOT NULL` |
| `answers` | `id PK`, `question_id FK`, `chosen_index INT`, `correct BOOL`, `answered_at` |
| `ce_records` | `id PK`, `session_id FK UNIQUE`, `pdf_storage_key`, `issued_at` |
| `openai_cost_ledger` | `id PK`, `year_month CHAR(7)`, `usd NUMERIC`, `request_count INT`, `updated_at` |

## Indexes
- `users(email)` UNIQUE.
- `courses(org_id, status)`.
- `sources(course_id, status)`.
- `chunks(source_id, page)`.
- `sessions(user_id, course_id, started_at DESC)`.
- `questions(session_id)`.
- `refresh_tokens(user_id)`, `refresh_tokens(expires_at)`.

## Constraints
- `questions.source_doc_id`, `source_page`, `source_span` **NOT NULL**.
- `questions.citation_overlap` CHECK `>= 0 AND <= 1`.
- `courses.pass_pct` CHECK `>= 50 AND <= 100`.
- `refresh_tokens.replaced_by_jti` FK to `refresh_tokens.jti` (self).

## Retention
- `refresh_tokens` cleaned hourly when `expires_at < now()`.
- `sessions`, `questions`, `answers`, `ce_records` indefinite (CE compliance).
- `openai_cost_ledger` indefinite (financial audit).

## Migration Safety
- Default additive. Backfills run as part of migration only when reversible.
- Non-reversible migrations get `# reversible: no` in the docstring and
  require S6 approval outside local.

## Required Tests
- Repository round-trip per table.
- A failing test that proves `Question` row with NULL citation column is
  rejected by the DB (`IntegrityError`).
- `refresh_tokens` chain revocation test.

## Acceptance Criteria
- [ ] `alembic upgrade head` from empty DB succeeds.
- [ ] Round-trip tests pass for every table.
- [ ] Citation NOT NULL test fails-then-passes after constraint added.
