# SPEC-003 — API Contracts

**Status:** Accepted
**Owner:** founding-eng
**Date:** 2026-01
**Linked Roadmap Phase:** P3
**Linked ExecPlans:** EP-004, EP-006

## User-Visible Goal
A stable HTTP/JSON contract that the Next.js client and any future client
can rely on, with consistent error shapes and authorization.

## Non-Goals
- gRPC. GraphQL.
- Public third-party API at launch.

## Conventions
- Base path: `/api/...` (except `/auth/...`, `/healthz`, `/readyz`, `/metrics`).
- Auth: `Authorization: Bearer <jwt>` except allowlist (`/auth/login`,
  `/auth/register`, `/auth/refresh`, `/healthz`, `/readyz`, `/metrics`).
- Errors: RFC 7807 `application/problem+json` with `type`, `title`,
  `status`, `detail`, `instance`, `request_id`.
- Rate limits per `SECURITY.md`.

## Routes
| Method | Path | Auth | Body | Response | Errors |
|---|---|---|---|---|---|
| POST | `/auth/register` | none | `RegisterDTO {email, password}` | 201 `UserDTO` | 422, 429 |
| POST | `/auth/login` | none | `LoginDTO {email, password}` | 200 `AccessTokenDTO` + Set-Cookie `refresh` | 401, 429 |
| POST | `/auth/refresh` | refresh cookie | (none) | 200 `AccessTokenDTO` + rotated cookie | 401, 429 |
| POST | `/auth/logout` | refresh cookie | (none) | 204 | 401 |
| GET | `/api/courses` | jwt | — | 200 `CourseListDTO` | 401 |
| GET | `/api/courses/{id}` | jwt | — | 200 `CourseDetailDTO` (`CourseDTO` + `sources[]`) | 401, 404 |
| POST | `/api/courses` | jwt (admin) | `CourseCreateDTO {title, n_questions>=1, pass_pct 50-100}` | 201 `CourseDTO` | 401, 403, 422 |
| POST | `/api/courses/{id}/sources` | jwt (admin) multipart | file | 202 `SourceDTO` | 401, 403, 413, 415, 422 |
| GET | `/api/sources/{id}/status` | jwt | — | 200 `SourceStatusDTO` | 401, 404 |
| POST | `/api/sessions/{course_id}/start` | jwt | (none) | 201 `SessionDTO` (Q list each with `citation_url`) | 401, 404, 409, 503 |
| GET | `/api/sessions/{id}` | jwt | — | 200 `SessionDTO` | 401, 404 |
| POST | `/api/sessions/{id}/answers` | jwt | `AnswerDTO {question_id, chosen_index}` | 200 `AnswerResultDTO` | 401, 404, 409, 422 |
| GET | `/api/ce-records/{id}` | jwt | — | 200 `CERecordDTO` + PDF download URL | 401, 404 |
| GET | `/healthz` | none | — | 200 `{"status":"ok"}` | (always 200 if up) |
| GET | `/readyz` | none | — | 200 `{"db":true,"faiss":true,"llm":true}` else 503 | 503 |
| GET | `/metrics` | scrape | — | 200 Prometheus text | — |

## DTO Shapes (selected)
- `AccessTokenDTO`: `{ access_token: str, token_type: "Bearer", expires_in: int }`
- `QuestionDTO`: `{ id, text, options[], citation: {doc_id, page, span, url} }`
- `SourceDTO`: `{ id, course_id, filename (<=255 chars), bytes, sha256, status, created_at }`
- `AnswerDTO`: `{ question_id: nonblank string (<=36 chars), chosen_index: int >= 0 }`
- `CitationPreviewDTO`: `{ doc_id: nonblank string (<=36 chars), page, span, source_filename, passage }`
- `CourseCreateDTO`: `{ title: nonblank string (<=255 chars), n_questions: int >= 1, pass_pct: 50-100 }`
- `CourseDetailDTO`: `CourseDTO` plus `sources[]` for the detail page; the
  list endpoint continues to use `CourseListDTO`.
- `AnswerResultDTO`: `{ correct: bool, correct_index: int, rationale: str,
  citation: {...}, session_progress: {answered, total} }`

## OpenAPI
Snapshot at `apps/api/openapi.json`. Drift fails
`tests/integration/test_openapi_snapshot.py`.

## Required Tests
- One contract test per route.
- Authz matrix (`test_authz.py`): every route returns 401/403 correctly
  when unauthenticated / cross-tenant.
- Error-shape test (`test_error_shape.py`): every error path returns
  `application/problem+json`.

## Acceptance Criteria
- [ ] All contract tests pass.
- [ ] OpenAPI snapshot committed.
- [ ] Authz matrix green.
