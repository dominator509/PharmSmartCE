# EP-006 — Auth, Security, Permissions

**Phase:** P5

## 1. Purpose / Big Picture
Implement full authentication, authorization, rate limits, security headers, and the OpenAI cost cap circuit breaker per `SPEC-005` and `SECURITY.md`.

## 2. Scope
- Argon2id password hashing
- JWT issue/verify (15-minute HS256)
- Opaque refresh token with rotation and chain revocation
- slowapi rate limiting
- SecurityHeadersMiddleware (HSTS, X-Frame-Options DENY, CSP)
- Per-resource authz (cross-tenant returns 404)
- OpenAI cost cap circuit breaker

## 3. Non-goals
- SSO/MFA/magic links (post-launch)
- UI changes (EP-005)

## 4. Context and Orientation
Builds on EP-004 stubs. Now wires real implementations.

## 5. Files to Read First
- `AGENTS.md`
- `SECURITY.md`
- `.agent/specs/SPEC-005-auth-and-permissions.md`

## 6. Files to Change
- `apps/api/app/services/auth/password.py`
- `apps/api/app/services/auth/jwt.py`
- `apps/api/app/services/auth/refresh.py`
- `apps/api/app/services/auth/service.py`
- `apps/api/app/api/middleware/__init__.py`
- `apps/api/app/api/middleware/rate_limit.py`
- `apps/api/app/api/middleware/security_headers.py`
- `apps/api/app/api/deps.py`
- `apps/api/app/services/generation/cost_cap.py`
- `apps/api/app/main.py`
- `apps/api/tests/integration/security/test_authz_matrix.py`
- `apps/api/tests/integration/security/test_refresh_rotation.py`
- `apps/api/tests/integration/security/test_chain_revocation.py`
- `apps/api/tests/integration/security/test_rate_limit.py`
- `apps/api/tests/integration/security/test_no_traceback_leak.py`
- `apps/api/tests/integration/security/test_security_headers.py`
- `apps/api/tests/integration/security/test_openai_cost_cap.py`

## 7. Interfaces and Contracts
AuthService implements `register`, `login`, `refresh`, `logout`. JWT carries `sub`, `org_id`, `jti`. Refresh tokens stored as sha256(opaque) in DB with `replaced_by_jti` chain. SecurityHeadersMiddleware adds standard headers. Cost cap reads `openai_cost_ledger` to make the circuit-breaker decision.

## 8. Milestones

### M1: Argon2id password hashing
- **Files to read:** `SECURITY.md`
- **Files to change:** `apps/api/app/services/auth/password.py`
- **Exact edits expected:** Use `argon2-cffi`. `hash_password(pw)` and `verify_password(hash, pw)` with parameters (time=2, memory=19456, parallelism=1, salt_len=16). Module-level constants for parameters.
- **Validation command:** `uv run --directory apps/api pytest tests/unit/services/test_password.py -q`
- **Expected result:** Hash/verify round-trip + slow-path timing > 5ms.
- **Recovery:** If hash too slow on CI, lower memory to 9216 and document in Decision Log.

### M2: JWT issue/verify
- **Files to read:** `SECURITY.md`, `.agent/specs/SPEC-005-auth-and-permissions.md`
- **Files to change:** `apps/api/app/services/auth/jwt.py`
- **Exact edits expected:** Use `python-jose` or `PyJWT`. Issue: 15-minute HS256 JWT with sub/org_id/jti/iss=pharmsmartce. Verify checks iss, exp.
- **Validation command:** `uv run --directory apps/api pytest tests/unit/services/test_jwt.py -q`
- **Expected result:** Issue + verify round-trip + expiry test passes.
- **Recovery:** If clock skew issues, allow 10s leeway and document.

### M3: Refresh token rotation + chain revocation
- **Files to read:** `.agent/specs/SPEC-005-auth-and-permissions.md`
- **Files to change:** `apps/api/app/services/auth/refresh.py`, `apps/api/app/services/auth/service.py`, `apps/api/app/repositories/refresh_token_repo.py`
- **Exact edits expected:** Refresh service creates opaque token (`secrets.token_urlsafe(32)`); stores sha256 in DB; on refresh, revokes old jti and chains `replaced_by_jti`; on reuse of revoked jti, revokes the entire chain.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/security/test_refresh_rotation.py tests/integration/security/test_chain_revocation.py -q`
- **Expected result:** Both tests pass.
- **Recovery:** If race conditions, lock on (user_id, jti) UPDATE.

### M4: Rate limiting + security headers middleware
- **Files to read:** `SECURITY.md`
- **Files to change:** `apps/api/app/api/middleware/__init__.py`, `apps/api/app/api/middleware/rate_limit.py`, `apps/api/app/api/middleware/security_headers.py`, `apps/api/app/main.py`
- **Exact edits expected:** slowapi limiter keyed by IP for /auth/* and by user for /api/*. SecurityHeadersMiddleware adds HSTS, X-Content-Type-Options, X-Frame-Options DENY, Referrer-Policy, CSP self+api.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/security/test_rate_limit.py tests/integration/security/test_security_headers.py -q`
- **Expected result:** Rate limit + headers tests pass.
- **Recovery:** If CSP breaks frontend, narrow CSP only as required for the violation; do not allow `unsafe-inline`.

### M5: Per-resource authz + 404-vs-403 policy
- **Files to read:** `.agent/specs/SPEC-005-auth-and-permissions.md`
- **Files to change:** `apps/api/app/api/deps.py`
- **Exact edits expected:** Dependencies `require_admin`, `require_course_access(course_id)`. Cross-tenant lookup returns 404, not 403.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/security/test_authz_matrix.py -q`
- **Expected result:** Authz matrix green.
- **Recovery:** If a route is missing the dep, add it; do not loosen the test.

### M6: OpenAI cost cap circuit breaker
- **Files to read:** `SECURITY.md`, `OBSERVABILITY.md`
- **Files to change:** `apps/api/app/services/generation/cost_cap.py`, `apps/api/app/services/generation/service.py`
- **Exact edits expected:** Before each OpenAI call, GenerationService asks `cost_cap.allow()`. If monthly spend ≥ cap, returns False; service falls back to local LLM and emits `openai_cap_reached` metric. At 80%, emits `openai_cap_warn_80`.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/security/test_openai_cost_cap.py -q`
- **Expected result:** Cap test passes (fallback exercised).
- **Recovery:** If counter race, take SELECT FOR UPDATE on the ledger row before write.

### M7: No-traceback-leak test
- **Files to read:** `.agent/specs/SPEC-006-error-handling.md`
- **Files to change:** `apps/api/tests/integration/security/test_no_traceback_leak.py`
- **Exact edits expected:** Force a route to raise an uncaught exception (via test-only inject). Assert response body has no `Traceback`, no file paths, no internal class names.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/security/test_no_traceback_leak.py -q`
- **Expected result:** Test passes.
- **Recovery:** If a leak path remains, ensure the 500 handler returns a generic detail and logs full traceback to logs only.

## 9. Concrete Steps
Execute milestones in order. After each: run validation, verify expected,
tick `Progress`, append one-line note. Apply bounded-retry (AGENTS §7) on
any failure. Continue autonomously. Stop only under STOP conditions.

## 10. Validation and Acceptance
- All milestone validations pass.
- `scripts/verify.sh` exit 0.
- Acceptance criteria:
  - [ ] `scripts/security-check.sh` clean
  - [ ] All security tests pass
  - [ ] Refresh rotation + chain revocation tested
  - [ ] OpenAI cost cap exercised in test
  - [ ] Security headers present

## 11. Idempotence and Recovery
Tests are idempotent. Tokens are scoped per-test by issuing fresh ones.

## 12. Progress
- [ ] M1: Argon2id password hashing
- [ ] M2: JWT issue/verify
- [ ] M3: Refresh token rotation + chain revocation
- [ ] M4: Rate limiting + security headers middleware
- [ ] M5: Per-resource authz + 404-vs-403 policy
- [ ] M6: OpenAI cost cap circuit breaker
- [ ] M7: No-traceback-leak test

## 13. Surprises & Discoveries
(empty — append entries here as they occur)

## 14. Decision Log
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
(to be filled at completion)
