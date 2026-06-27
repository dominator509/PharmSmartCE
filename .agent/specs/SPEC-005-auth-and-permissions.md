# SPEC-005 — Auth & Permissions

**Status:** Accepted
**Owner:** founding-eng
**Date:** 2026-01
**Linked Roadmap Phase:** P5
**Linked ExecPlans:** EP-006

## User-Visible Goal
Users authenticate with email + password and stay logged in across visits
without exposing tokens to JavaScript.

## Non-Goals
- SSO at launch.
- MFA at launch (room reserved in schema).
- Magic links at launch.

## Registration
- Email format validated.
- Password length ≥ 12; no max cap; no composition rules.
- Argon2id (time=2, memory=19456, parallelism=1, salt=16B).
- Created `User` belongs to its own new `Org` unless invited (post-launch).

## Login
- Rate-limited (10/min per IP, 5/min per email).
- On success: 200 + JWT (15 min) + Set-Cookie `refresh` (httpOnly, Secure,
  SameSite=Lax, 30 d, `Path=/api/auth`).
- On failure: 401; counter incremented; same error for unknown email vs bad
  password.

## Refresh
- Cookie-only. Server validates JTI, rotates token, returns new pair.
- Reuse of revoked JTI revokes the **entire chain** for that user.

## Logout
- Revokes the current refresh token; clears cookie.

## Permissions / Roles
- `admin` (per Org): create Courses, upload Sources.
- `member` (per Org): take CE sessions.
- Per-resource: `course.org_id == user.org_id` required for any access.
  Cross-tenant lookup returns 404 (no enumeration).

## Security Requirements
Per `SECURITY.md`: rate limits, security headers, log redaction.

## Required Tests
- Argon2id round-trip + slow-path test.
- Login rate-limit test.
- Refresh rotation + chain-revocation test.
- Authz matrix: every route + each role.
- 404-vs-403 cross-tenant test.

## Acceptance Criteria
- [ ] All security tests pass.
- [ ] `scripts/security-check.sh` clean.
- [ ] Manual penetration check: no unauthenticated access to non-allowlisted
      routes.
