# SECURITY.md

## Goals
Protect user credentials and refresh tokens. Protect uploaded source
documents. Ensure the LLM cannot be coerced (via injection in uploaded
content) to ignore grounding. Ensure generated questions cite real,
verifiable sources. Prevent runaway costs from optional paid LLM providers.

## Threat Model

| Asset | Threat | Mitigation |
|---|---|---|
| User creds | Account takeover | Argon2id; rate-limited login; ≥12 char policy |
| Refresh tokens | Theft via XSS | httpOnly+Secure+SameSite=Lax cookie; rotation; revocation table |
| JWT secret | Compromise | Deploy platform secret store; rotation procedure |
| Source PDFs | Unauthorized read | Authz `course.org_id == user.org_id`; signed S3 URLs short TTL |
| LLM prompt | Injection in uploaded PDFs | Delimited chunks; locked system prompt; pre-gen regex flagger; flagged chunk fails closed |
| Output | Citation forgery / hallucination | `CitationValidator` overlap ≥ `CITATION_MIN_OVERLAP_RATIO`; NOT NULL citation cols; UI hyperlink to source viewer |
| OpenAI billing | Runaway cost | `OPENAI_MONTHLY_USD_CAP`; circuit breaker → fallback at 100%; alert at 80% |
| IDOR | Forced access | Authz in services; integration test matrix |
| Dependency CVE | Supply chain | `pip-audit` + `pnpm audit` in CI; Dependabot weekly |
| Logs | Secret leakage | structlog `RedactProcessor` |
| File uploads | Malicious payloads | `python-magic` sniff; PDF/DOCX allowlist; 50 MB max; optional clamav |

## Authentication
- **Hashing:** Argon2id `time_cost=2, memory_cost=19456 (≈19 MiB),
  parallelism=1, salt_len=16`.
- **Password policy:** length ≥ 12; no max cap; no composition rules.
- **Access token:** JWT HS256, 15-minute TTL, `iss=pharmsmartce`,
  `sub=user_id`, `org_id`, `jti`.
- **Refresh token:** opaque 256-bit. `sha256` in DB row
  `(user_id, jti, expires_at, revoked_at, replaced_by_jti)`. Cookie:
  `HttpOnly; Secure; SameSite=Lax; Max-Age=2592000; Path=/api/auth`.
- **Rotation:** every successful `/auth/refresh` revokes old jti and chains
  `replaced_by_jti`. Reuse of revoked jti revokes the **entire chain**.

## Authorization
Default-deny. Auth allowlist: `/auth/login`, `/auth/register`,
`/auth/refresh`, `/healthz`, `/readyz`, `/metrics`. Per-resource checks
in services. Cross-tenant lookup returns 404 not 403 (avoid enumeration).

## Input Validation
All HTTP bodies via Pydantic with `extra='forbid'`. Domain invariants raise
`DomainError` → 422.

## Output Encoding
React: never `dangerouslySetInnerHTML`. Source passages plain text with CSS
whitespace preservation. API JSON only.

## Secret Management
Env vars at runtime from deploy platform secret store. Never in repo.
`.env.example` schema only.

## Dependency Security
`scripts/dependency-audit.sh` runs `pip-audit` + `pnpm audit`. CI fails on
`high`/`critical` without justification in `apps/api/.audit-allow.txt` /
`apps/web/.audit-allow.txt`. Dependabot weekly.

## Logging Redaction
Redacted: `password`, `password_hash`, `authorization`, `cookie`,
`set-cookie`, `refresh_token`, `access_token`, `jwt`, `api_key`,
`openai_api_key`, `s3_secret_access_key`; full bodies of `POST /auth/*`
and `POST /api/courses/*/sources`. Implementation:
`apps/api/app/observability/logging.py::RedactProcessor`.

## Data Protection
TLS everywhere. Postgres `sslmode=require`. S3 over HTTPS with SSE-S3.

## API Security
- Rate limits (native in-process limiter): `/auth/login` 10/min per IP +
  5/min per email; `/auth/register` 5/min per IP; `/api/*` default 30/min per
  user.
- CORS: allowlist from `CORS_ALLOWED_ORIGINS`. No wildcard outside local.
- Security headers (`SecurityHeadersMiddleware`):
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Content-Security-Policy: default-src 'self'; img-src 'self' data:;
    connect-src 'self' <api_origin>`

## CSRF / Cookies
Refresh cookie is `SameSite=Lax`. Access token (JWT) in `Authorization`
header → CSRF not exploitable for API.

## File Upload
- Allowed: `application/pdf`,
  `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.
- Order: size ≤ `UPLOAD_MAX_BYTES` → magic-byte sniff (`python-magic`) →
  reject if extension/sniff/declared MIME disagree.
- Optional clamav adapter (off by default).

## Prompt Injection Defense
- System prompt is a module-level constant in `grounded_llm.py`.
- Chunks wrapped:
  ```
  <<<context_start id="{doc_id}:{page}:{span}">>>
  {chunk_text}
  <<<context_end>>>
  ```
- Pre-generation `InjectionDetector`:
  ```
  r"ignore (the )?(previous|above|prior) instructions?"
  r"<<<\s*context_(start|end)\s*>>>"
  r"^\s*(system|assistant)\s*:"
  r"you are (now )?(a|an) .{0,80} (assistant|ai|model)"
  ```
- Flagged chunk skipped; retrieval continues. If > 25% chunks flagged →
  source `quarantined`; author notified.

## Security Checklist (per release)
- [ ] `scripts/security-check.sh` clean.
- [ ] `scripts/dependency-audit.sh` clean or allowlisted with reason.
- [ ] No new env vars carry secrets without redaction.
- [ ] No new routes in auth allowlist.
- [ ] Rate limits unchanged or tightened.
- [ ] Cookie flags unchanged or tightened.
- [ ] CSP unchanged or tightened.

## STOP Conditions
- **S3.** Enabling `LLM_PROVIDER=openai` in any environment.
- **S3.** Raising `OPENAI_MONTHLY_USD_CAP`.
- **S3.** Disabling the `InjectionDetector` or `CitationValidator`.
- **S3.** Adding a new accepted upload format.
- **S2.** Rotating `JWT_SECRET` / `REFRESH_SECRET` in non-local envs without
  the documented procedure.
