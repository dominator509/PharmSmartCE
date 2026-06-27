# DECISIONS.md — Architecture Decision Records

This file is the ADR index. New ADRs use `.agent/templates/adr-template.md`.
Status values: `Proposed`, `Accepted`, `Deprecated`, `Superseded`.

## ADR Index

| ID | Title | Status | Date | Owner |
|---|---|---|---|---|
| ADR-001 | Backend: FastAPI + Pydantic v2 + SQLAlchemy 2 | Accepted | 2026-01 | founding-eng |
| ADR-002 | Frontend: Next.js 14 (App Router) + TS + Tailwind | Accepted | 2026-01 | founding-eng |
| ADR-003 | DB: PostgreSQL 15 + FAISS (file) | Accepted | 2026-01 | founding-eng |
| ADR-004 | LLM: llama-cpp-python with GGUF Q4_K_M (CPU only) | Accepted | 2026-01 | founding-eng |
| ADR-005 | RAG-only grounding; no fine-tuning at launch | Accepted | 2026-01 | founding-eng |
| ADR-006 | Auth: Argon2id + JWT (15m) + opaque refresh (httpOnly) | Accepted | 2026-01 | founding-eng |
| ADR-007 | Package managers: uv + pnpm | Accepted | 2026-01 | founding-eng |
| ADR-008 | CI/CD: GitHub Actions | Accepted | 2026-01 | founding-eng |
| ADR-009 | Strict citation invariant on every persisted Question | Accepted | 2026-01 | founding-eng |
| ADR-010 | OpenAI adapter OFF by default; cost cap enforced | Accepted | 2026-01 | founding-eng |

---

## ADR-001 — Backend: FastAPI + Pydantic v2 + SQLAlchemy 2
**Context.** Need Python backend (LLM ecosystem). Must be async (LLM is slow),
strong validation, mature ORM + migrations.
**Decision.** FastAPI 0.115+, Pydantic v2, SQLAlchemy 2 async, Alembic.
**Alternatives.** Django (heavier, sync-first); Flask (no built-in validation);
Litestar (smaller community); Node/Express (splits language from LLM tooling).
**Consequences.** Auto OpenAPI; DI via `Depends`; async-only discipline.
**Status.** Accepted. **Date.** 2026-01. **Owner.** founding-eng.

## ADR-002 — Frontend: Next.js 14 App Router + TS + Tailwind
**Context.** SSR for SEO; auth via httpOnly cookie easier with server; fast iteration.
**Decision.** Next.js 14 App Router + TypeScript + Tailwind. State: React Query.
**Alternatives.** Vite SPA (no SSR); Remix; SvelteKit.
**Consequences.** Free hosting; slight Next.js lock-in.
**Status.** Accepted. **Date.** 2026-01. **Owner.** founding-eng.

## ADR-003 — DB: PostgreSQL 15 + FAISS (file)
**Context.** Relational + vector store; want cheap managed.
**Decision.** Postgres 15 (managed) + FAISS index file per course; pgvector
reserved for v2.
**Alternatives.** pgvector v1; Pinecone/Weaviate (paid); SQLite.
**Consequences.** Two stores. FAISS is rebuildable from sources →
non-authoritative.
**Status.** Accepted. **Date.** 2026-01. **Owner.** founding-eng.

## ADR-004 — LLM: llama-cpp-python with GGUF Q4_K_M (CPU only)
**Context.** Required CPU-only inference.
**Decision.** Default 7–8B instruct GGUF Q4_K_M via `llama-cpp-python`.
Threads = `nproc`. Weights downloaded to `models/` by `install.sh`.
**Alternatives.** Mistral-7B-Instruct, Phi-3-mini, ONNX Runtime.
**Consequences.** Slow inference (~30s/6 questions on 4 vCPU).
**Status.** Accepted. **Date.** 2026-01. **Owner.** founding-eng.

## ADR-005 — RAG-only; no fine-tuning at launch
**Context.** Clinical accuracy required; fine-tuning expensive + risky.
**Decision.** RAG only. Delimited chunks + locked system prompt. Citation
validator rejects misalignment.
**Alternatives.** LoRA per course (cost); prompt-only (no contract).
**Consequences.** Quality bound by retrieval quality.
**Status.** Accepted. **Date.** 2026-01. **Owner.** founding-eng.

## ADR-006 — Auth: Argon2id + JWT (15m) + opaque refresh (httpOnly, 30d)
**Context.** No HIPAA but credentials must be safely stored; UI needs session
persistence without exposing tokens to JS.
**Decision.** Argon2id (time=2, memory=19MB, parallelism=1, salt=16B). JWT
HS256 15m. Refresh: opaque 256-bit, sha256 in DB, httpOnly+Secure+SameSite=Lax
cookie. Rotation on refresh; reuse revokes the chain.
**Alternatives.** OAuth third-party; bcrypt; long-lived JWT.
**Consequences.** Refresh table grows; nightly cleanup needed.
**Status.** Accepted. **Date.** 2026-01. **Owner.** founding-eng.

## ADR-007 — Package managers: uv + pnpm
**Context.** Want fast, deterministic, lockfile installs.
**Decision.** `uv` (Python), `pnpm` (Node).
**Alternatives.** poetry, rye, npm/yarn.
**Consequences.** Slight onboarding cost.
**Status.** Accepted. **Date.** 2026-01. **Owner.** founding-eng.

## ADR-008 — CI/CD: GitHub Actions
**Context.** Repo on GitHub; need CI per PR + tag-based deploys.
**Decision.** GitHub Actions; workflows in `.github/workflows/`.
**Alternatives.** CircleCI, GitLab CI, Buildkite.
**Consequences.** Free tier sufficient at launch.
**Status.** Accepted. **Date.** 2026-01. **Owner.** founding-eng.

## ADR-009 — Strict citation invariant on every persisted Question
**Context.** Clinical claims without citation are a launch-blocker risk.
**Decision.** NOT NULL columns `source_doc_id`, `source_page`, `source_span`
on `questions`. Domain constructor raises on empty. `CitationValidator` runs
before persistence. UI renders as clickable hyperlink.
**Alternatives.** Soft string citation (rejected).
**Consequences.** Some generations discarded; capped by
`GENERATION_RETRY_BUDGET`.
**Status.** Accepted. **Date.** 2026-01. **Owner.** founding-eng.

## ADR-010 — OpenAI OFF by default; cost cap enforced
**Context.** Optional paid LLM allowed if costs low; risk of runaway bill.
**Decision.** `LLM_PROVIDER` defaults to `llama_cpp`. `openai` requires
`OPENAI_API_KEY` and `OPENAI_MONTHLY_USD_CAP`. Counter
`openai_cost_usd_total`. Circuit breaker: at 100% cap → fallback to local;
at 80% → alert.
**Alternatives.** No cap; hard kill.
**Consequences.** Operator must set the cap.
**Status.** Accepted. **Date.** 2026-01. **Owner.** founding-eng.
