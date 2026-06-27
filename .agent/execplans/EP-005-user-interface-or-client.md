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
- [ ] M1: API client lib + auth bridge
- [ ] M2: Auth pages
- [ ] M3: Courses pages
- [ ] M4: Session page + QuestionView + CitationDrawer
- [ ] M5: Results page + CE record download
- [ ] M6: axe-core accessibility

## 13. Surprises & Discoveries
(empty — append entries here as they occur)

## 14. Decision Log
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
(to be filled at completion)
