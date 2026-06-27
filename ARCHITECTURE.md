# ARCHITECTURE.md

## Purpose
Canonical structural rules of PharmSmartCE: what each layer does, who may
call whom, where data flows, and what is forbidden. If a proposed change
violates this document, update this document first (with an ADR) or do not
make the change.

## System Overview
Three-tier SaaS: Next.js web → FastAPI API → Postgres + FAISS + llama.cpp +
S3-compatible storage. CPU-only LLM is default; OpenAI adapter is optional.

```
Pharmacist ─► Next.js 14 ──REST/JSON──► FastAPI
                                         ├─ routes
                                         ├─ services (incl. generation)
                                         ├─ domain (pure)
                                         ├─ repositories ─► Postgres
                                         └─ adapters     ─► FAISS, llama.cpp,
                                                            OpenAI (opt), S3
```

## Repository Map
```
/
├── apps/
│   ├── api/                          FastAPI backend (Python 3.11)
│   │   ├── app/
│   │   │   ├── main.py               FastAPI app factory; mounts routers
│   │   │   ├── config.py             ONLY place that reads env vars
│   │   │   ├── api/                  HTTP routes / deps / DTOs / handlers
│   │   │   ├── services/
│   │   │   │   ├── generation/       RAG + grounded LLM + citation validator
│   │   │   │   ├── ingest/           PDF/DOCX → chunks → embed → FAISS
│   │   │   │   ├── auth/             Login, refresh, password hashing
│   │   │   │   ├── session/          Session lifecycle
│   │   │   │   └── ports/            Adapter Protocols
│   │   │   ├── domain/               Pure entities + invariants (NO I/O)
│   │   │   ├── repositories/         SQLAlchemy (ONLY SQL location)
│   │   │   ├── adapters/
│   │   │   │   ├── llm/              llama_cpp, openai, fake
│   │   │   │   ├── embeddings/       sentence_transformers
│   │   │   │   ├── storage/          s3, local_fs, faiss_store
│   │   │   │   └── email/            smtp
│   │   │   ├── observability/        logging, metrics, sentry
│   │   │   ├── workers/              ingest, generation
│   │   │   └── cli/                  seed_dev, smoke, tail_logs, reingest
│   │   ├── alembic/
│   │   ├── tests/{unit,integration,e2e,fixtures}
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   └── web/                          Next.js 14 frontend
│       ├── app/                      App Router pages
│       ├── components/
│       ├── lib/                      API client + auth helpers
│       ├── tests/{unit,e2e}
│       ├── package.json
│       └── Dockerfile
├── packages/shared/                  TS types from OpenAPI
├── infra/                            docker-compose, fly.toml files
├── models/                           GITIGNORED — *.gguf
├── var/uploads/                      GITIGNORED — local PDF uploads
├── scripts/                          Shell entrypoints
├── .agent/                           Plans, specs, prompts, checklists
└── (root markdown docs)
```

## Layer Responsibilities
| Layer | Responsibility |
|---|---|
| `api/` (routes) | HTTP transport; Pydantic validation; call services; map exceptions → problem+json |
| `services/` | Business workflows; orchestrate domain + repositories + adapters via ports |
| `domain/` | Pure entities, value objects, invariants. NO I/O. NO framework imports |
| `repositories/` | SQLAlchemy queries; one repo per aggregate root |
| `adapters/` | External integrations; implement `ports/` Protocols |
| `observability/` | structlog, Prometheus registry, OTel hooks, Sentry |
| `workers/` | Background tasks (ingest, generation) |
| `cli/` | Operator entrypoints |

## Dependency / Import Rules
| From → To | Allowed? |
|---|---|
| `api` → `services` | ✅ |
| `api` → `domain` | ✅ (DTO ↔ entity) |
| `api` → `repositories` | ❌ |
| `api` → `adapters` | ❌ |
| `services` → `domain` | ✅ |
| `services` → `repositories` | ✅ |
| `services` → `ports` | ✅ |
| `services` → `adapters` | ❌ (use ports) |
| `domain` → anything else | ❌ |
| `repositories` → `domain` | ✅ |
| `adapters` → `domain` | ✅ (read-only types) |

Enforced by `import-linter` config in `apps/api/pyproject.toml`.

## Runtime Flow — Question Generation
1. Client `POST /api/sessions/{course_id}/start` with JWT.
2. Auth dep → `User`.
3. Route → `GenerationService.start_session(user, course_id)`.
4. Service loads `Course` via `CourseRepo`.
5. `RAGRetriever.retrieve(course, n, seed=user_id+session_id)` → list of `Chunk`.
6. For each chunk: `GroundedLLM.generate_question(chunk)` — prompt wraps chunk
   in `<<<context_start>>>...<<<context_end>>>`; system prompt forbids
   answering outside context.
7. `CitationValidator.validate(question, chunk)` — overlap ≥
   `CITATION_MIN_OVERLAP_RATIO`. Fail → discard, retry up to
   `GENERATION_RETRY_BUDGET`.
8. Persist via `SessionRepo` with NOT NULL citation fields.
9. Return `SessionDTO`.

## Data Flow — Source Ingest
1. `POST /api/courses/{id}/sources` (multipart) → validate magic bytes + size
   → S3 via `StorageAdapter`.
2. `IngestService.enqueue(source_id)`.
3. Worker: extract text per page → chunk (token-aware, 512/64) → embed →
   FAISS index file `var/faiss/{course_id}.index` + metadata JSONL.
4. `SourceStatusRepo.mark_ready(source_id)`.

## State Management Rules
- Server is source of truth for sessions, questions, grading.
- Client uses React Query for cache; mutations refetch authoritative state.
- No client-side question persistence beyond ephemeral cache.

## Persistence Boundaries
Only `app/repositories/*` issues SQL. Services receive repositories by
constructor injection. Transactional boundaries at service-method level.

## External Integration Boundaries
All external calls via `app/adapters/*`. Each adapter implements a Protocol
in `app/services/ports/`. Concrete adapter selection in `app/main.py` via
`Settings`.

## Security Boundaries
Auth dependency at router level for all routers except `/auth/login`,
`/auth/register`, `/auth/refresh`, `/healthz`, `/readyz`, `/metrics`.
Per-resource authz in services. Secrets only in `app/config.py` via
`pydantic-settings`.

## Validation Boundaries
- HTTP: Pydantic with `extra='forbid'`.
- Domain: entity constructors raise `DomainError` on invariant violation.

## Error Handling Boundaries
Internal: `AppException` hierarchy (`NotFoundError`, `AuthError`,
`AuthorizationError`, `ValidationError`, `RateLimitError`,
`ExternalServiceError`, `GroundingError`, `ConflictError`).
HTTP: handlers map each → RFC 7807 problem+json. Stack traces never in
responses; go to logs + Sentry.

## Observability Boundaries
Middleware assigns `request_id` (ULID), binds to structlog. Services emit
structured events with consistent fields. Adapters emit `duration_ms` metric.

## Architectural Invariants
- **I1.** No LLM call outside `app/services/generation/grounded_llm.py`.
- **I2.** Every persisted `Question` has non-null `source_doc_id`,
  `source_page`, `source_span` (NOT NULL + service invariant).
- **I3.** Raw SQL forbidden outside `app/repositories/*`.
- **I4.** `os.environ` / `os.getenv` forbidden outside `app/config.py`.
- **I5.** `print()` forbidden in non-CLI code. Use structlog.
- **I6.** Route handlers may not call >1 repository write. Multi-write goes
  through a service.
- **I7.** `app/domain/*` may not import from `app/api`, `app/repositories`,
  `app/adapters`, `app/services`.
- **I8.** Every adapter implements a Protocol in `app/services/ports/`.
- **I9.** Every background task accepts/persists an idempotency key; reruns
  are no-ops after success.
- **I10.** Retrieval result fed to LLM MUST be ≤ `RAG_MAX_CONTEXT_TOKENS`.

## Forbidden Architecture Moves
- F1. Business logic in routes.
- F2. SQL in services.
- F3. `requests`/`httpx` outside adapters.
- F4. New top-level directory without ADR.
- F5. New external dependency without ADR.
- F6. Removing the citation validator.
- F7. Disabling the OpenAI cost cap to unblock a feature.

## How to Add a New Feature
1. Pick/create an ExecPlan in `.agent/execplans/`.
2. Read the relevant spec; if behavior undefined, update spec first.
3. Add/update domain entities.
4. Add a service method.
5. Add a repository method if persistence needed.
6. Add an HTTP route.
7. Add Pydantic DTOs.
8. Tests in lowest layer that exercises the behavior.
9. Update OpenAPI snapshot; regenerate TS types.
10. Run `scripts/verify.sh`.

## How to Add a New Dependency
1. Justify (AGENTS §8).
2. Pin in `pyproject.toml` / `package.json`.
3. `scripts/install.sh`.
4. `scripts/dependency-audit.sh`.
5. ADR if non-trivial.

## How to Modify the Data Schema
1. Update SQLAlchemy model.
2. `alembic revision --autogenerate -m "..."`.
3. Review generated SQL by hand.
4. Update `SPEC-002-data-model.md`.
5. Run integration suite locally.
6. Non-reversible? STOP S6 note in ExecPlan; explicit user approval for
   non-local envs.

## How to Add a New Integration
1. Define Protocol in `app/services/ports/`.
2. Implement adapter in `app/adapters/<integration>/`.
3. Add `FakeXAdapter` for tests.
4. Wire selection in `app/main.py` via `Settings`.
5. Add env var to `ENVIRONMENT.md` and `.env.example`.

## Architecture Review Checklist
- [ ] No imports violate the dependency table.
- [ ] No env reads outside `config.py`.
- [ ] No raw SQL outside repositories.
- [ ] No LLM calls outside `grounded_llm.py`.
- [ ] Citation invariant I2 respected.
- [ ] ADR exists for non-trivial choices.
- [ ] `import-linter` passes.
