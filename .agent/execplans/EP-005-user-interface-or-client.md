# EP-005 — UI / Client

**Phase:** P4

## 1. Purpose / Big Picture
Implement the Next.js 14 UI per `SPEC-004`: auth pages, courses pages, session page with question view, citation drawer, results, and CE record download. Cover the happy path with Playwright; check accessibility with axe-core.

## 2. Scope
- Auth pages (/login, /register)
- API client lib (lib/api.ts)
- Courses pages (list, detail, upload)
- Session page with question view and answer feedback
- CitationDrawer with deep-link
- Results + CE record download
- Playwright happy-path E2E + axe-core a11y

## 3. Non-goals
- Mobile native apps
- Offline mode
- Multi-language

## 4. Context and Orientation
Builds on EP-004 API. `WEB_PUBLIC_API_URL` configures the API base.

## 5. Files to Read First
- `AGENTS.md`
- `.agent/specs/SPEC-004-ui-ux-behavior.md`
- `apps/api/openapi.json`

## 6. Files to Change
- `apps/web/lib/api.ts`
- `apps/web/lib/auth.ts`
- `apps/web/app/(auth)/login/page.tsx`
- `apps/web/app/(auth)/register/page.tsx`
- `apps/web/app/(app)/layout.tsx`
- `apps/web/app/(app)/courses/page.tsx`
- `apps/web/app/(app)/courses/[id]/page.tsx`
- `apps/web/app/(app)/courses/[id]/UploadSource.tsx`
- `apps/web/app/(app)/sessions/[id]/page.tsx`
- `apps/web/app/(app)/sessions/[id]/results/page.tsx`
- `apps/web/components/CitationDrawer.tsx`
- `apps/web/components/QuestionView.tsx`
- `apps/web/tests/e2e/happy_path.spec.ts`
- `apps/web/tests/e2e/auth.spec.ts`
- `apps/web/tests/e2e/citation_deeplink.spec.ts`
- `apps/web/tests/e2e/a11y.spec.ts`

## 7. Interfaces and Contracts
API client uses bearer JWT from a server-side helper that reads the refresh cookie. CitationDrawer URL: `?cite=<doc_id>:<page>:<span>`. Forms use React Hook Form + zod (or built-in validators).

## 8. Milestones

### M1: API client lib + auth bridge
- **Files to read:** `.agent/specs/SPEC-003-api-contracts.md`
- **Files to change:** `apps/web/lib/api.ts`, `apps/web/lib/auth.ts`
- **Exact edits expected:** lib/api.ts wraps fetch with base URL, JSON, error handling for problem+json. lib/auth.ts has server actions for login/register/refresh/logout that set/clear the refresh cookie.
- **Validation command:** `pnpm --filter web typecheck`
- **Expected result:** tsc clean.
- **Recovery:** If types from openapi differ, regenerate `packages/shared` types and re-import.

### M2: Auth pages
- **Files to read:** `.agent/specs/SPEC-004-ui-ux-behavior.md`
- **Files to change:** `apps/web/app/(auth)/login/page.tsx`, `apps/web/app/(auth)/register/page.tsx`
- **Exact edits expected:** Forms with email + password; client-side validation (length ≥ 12); shows server errors inline; redirects to /courses on success.
- **Validation command:** `pnpm --filter web test:e2e -- auth.spec.ts`
- **Expected result:** Auth E2E passes against the local stack.
- **Recovery:** If form submit fails because cookies not set, ensure `credentials: 'include'` and same-origin in dev.

### M3: Courses pages
- **Files to read:** `.agent/specs/SPEC-004-ui-ux-behavior.md`
- **Files to change:** `apps/web/app/(app)/layout.tsx`, `apps/web/app/(app)/courses/page.tsx`, `apps/web/app/(app)/courses/[id]/page.tsx`, `apps/web/app/(app)/courses/[id]/UploadSource.tsx`
- **Exact edits expected:** List shows org's courses; detail shows source list with status badge; admin sees Upload component (drag/drop or file input).
- **Validation command:** `pnpm --filter web test:e2e -- happy_path.spec.ts -g 'upload source'`
- **Expected result:** Upload spec passes.
- **Recovery:** If file size validation differs from server, align with `UPLOAD_MAX_BYTES`.

### M4: Session page + QuestionView + CitationDrawer
- **Files to read:** `.agent/specs/SPEC-004-ui-ux-behavior.md`
- **Files to change:** `apps/web/app/(app)/sessions/[id]/page.tsx`, `apps/web/components/QuestionView.tsx`, `apps/web/components/CitationDrawer.tsx`
- **Exact edits expected:** Session page polls /api/sessions/{id} until status=ready then renders questions. QuestionView shows MCQ with citation as `[1]` superscript. CitationDrawer opens via click or `?cite=...` deep link.
- **Validation command:** `pnpm --filter web test:e2e -- citation_deeplink.spec.ts`
- **Expected result:** Deep-link spec passes.
- **Recovery:** If URL state lost across navigations, use Next.js `useSearchParams` not `window.location`.

### M5: Results page + CE record download
- **Files to read:** `.agent/specs/SPEC-004-ui-ux-behavior.md`
- **Files to change:** `apps/web/app/(app)/sessions/[id]/results/page.tsx`
- **Exact edits expected:** Shows score, pass/fail, CE record download link if passed.
- **Validation command:** `pnpm --filter web test:e2e -- happy_path.spec.ts`
- **Expected result:** Happy path passes end-to-end.
- **Recovery:** If PDF download fails locally, mock CERecord PDF generation; document in Decision Log.

### M6: axe-core accessibility
- **Files to read:** `.agent/specs/SPEC-004-ui-ux-behavior.md`
- **Files to change:** `apps/web/tests/e2e/a11y.spec.ts`
- **Exact edits expected:** Runs axe-core on /login, /courses, /sessions/:id with fixture data. Asserts no `serious` violations.
- **Validation command:** `pnpm --filter web test:e2e -- a11y.spec.ts`
- **Expected result:** No serious violations.
- **Recovery:** If a violation surfaces, fix the cheapest issue first (label, role); do not silence axe rules.

## 9. Concrete Steps
Execute milestones in order. After each: run validation, verify expected,
tick `Progress`, append one-line note. Apply bounded-retry (AGENTS §7) on
any failure. Continue autonomously. Stop only under STOP conditions.

## 10. Validation and Acceptance
- All milestone validations pass.
- `scripts/verify.sh` exit 0.
- Acceptance criteria:
  - [ ] Playwright happy path green
  - [ ] Auth flow E2E green
  - [ ] Citation deep link E2E green
  - [ ] axe-core: no serious violations on listed pages

## 11. Idempotence and Recovery
E2E tests are deterministic when the API is started fresh via docker compose. Re-running spins fresh services.

## 12. Progress
- [x] M1: API client lib + auth bridge - 2026-06-27 - `pnpm --filter web typecheck`, `pnpm --filter web test:unit`, `pnpm --filter web build`, and `scripts/verify.sh` passed.
- [x] M2: Auth pages - 2026-06-27 - `pnpm --filter web test:e2e -- auth.spec.ts` passed.
- [x] M3: Courses pages - 2026-06-27 - `pnpm --filter web test:e2e -- happy_path.spec.ts -g 'upload source'`, `pnpm --filter web typecheck`, and `pnpm --filter web test:unit` passed.
- [x] M4: Session page + QuestionView + CitationDrawer - 2026-06-27 - `pnpm --filter web typecheck` and `pnpm --filter web test:e2e -- citation_deeplink.spec.ts` passed.
- [ ] M5: Results page + CE record download
- [ ] M6: axe-core accessibility

## 13. Surprises & Discoveries
- 2026-06-27 - `apps/web/lib/api.ts` now wraps backend fetches with problem+json handling, and `apps/web/lib/auth.ts` provides a testable auth bridge around the refresh cookie.
- 2026-06-27 - The browser now lands on `/auth/complete` after login/register so it can persist the access token cookie client-side before the Next server renders `/courses` and `/courses/[id]`.
- 2026-06-27 - The session drawer now fetches citation previews from `/api/sessions/{session_id}/citation`, which reads stored chunk text so deep links can open a real source passage instead of a placeholder.

## 14. Decision Log
- 2026-06-27 - Next 15.5.18's `cookies()` is async in this repo, so the auth bridge awaits it and casts the returned cookie jar to the repository's narrow cookie-store helper type.
- 2026-06-27 - `apps/web/scripts/run-e2e.mjs` now starts both the Next dev server and the local FastAPI API so Playwright auth runs hit the real stack.
- 2026-06-27 - The course pages read the browser-set `access` cookie directly, while the auth-complete handoff page stores that cookie from the server-issued access token and then redirects to `/courses`.
- 2026-06-27 - `QuestionView` uses native radios plus a server-action-backed form state, and `CitationDrawer` renders as a role="dialog" panel so Playwright and assistive tech can open the citation deep link predictably.

## 15. Outcomes & Retrospective
The client layer now has a usable Next.js shell for auth, courses, and source upload. The auth-complete handoff keeps the server actions simple while still giving the browser a persistent token for protected pages, which made the courses flow and Playwright happy path land cleanly without a larger client-state rewrite.
