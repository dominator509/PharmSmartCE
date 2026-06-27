# SPEC-006 — Error Handling

**Status:** Accepted
**Owner:** founding-eng
**Date:** 2026-01
**Linked Roadmap Phase:** P3
**Linked ExecPlans:** EP-004

## User-Visible Goal
Errors are predictable, parseable, and never leak internals.

## Error Taxonomy
| Internal Exception | HTTP | `type` slug |
|---|---|---|
| `DomainError` | 422 | `domain-invariant` |
| `ValidationError` | 422 | `validation` |
| `NotFoundError` | 404 | `not-found` |
| `AuthError` | 401 | `unauthenticated` |
| `AuthorizationError` | 403 | `forbidden` |
| `ConflictError` | 409 | `conflict` |
| `RateLimitError` | 429 | `rate-limited` |
| `ExternalServiceError` | 502 | `upstream` |
| `GroundingError` | 503 | `grounding-failed` |
| `UnreadyError` | 503 | `not-ready` |
| (uncaught) | 500 | `internal` |

## Shape (RFC 7807)
```
{
  "type": "https://pharmsmartce.com/errors/<slug>",
  "title": "<short>",
  "status": <int>,
  "detail": "<safe message>",
  "instance": "<request path>",
  "request_id": "<ULID>"
}
```

## Logging
- Full traceback to logs (with redaction) + Sentry.
- Never to the response body.

## Retry Behavior
- Client (Next.js) retries idempotent GETs on 502/503 (exponential backoff,
  max 3).
- Server retries inside `GenerationService` only (per
  `GENERATION_RETRY_BUDGET`).
- No retries on 4xx anywhere.

## Required Tests
- `test_error_shape.py` — every taxonomy entry returns the expected
  problem+json.
- `test_no_traceback_leak.py` — induced 500 returns generic detail; logs
  contain traceback.

## Acceptance Criteria
- [ ] All taxonomy entries covered.
- [ ] No traceback ever appears in a response body.
