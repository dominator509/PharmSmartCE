# Frontend core
- Frontend lives in `apps/web` and uses the Next.js App Router with React, TypeScript, Tailwind, Playwright, and Vitest.
- Main routes: `/`, `/login`, `/register`, `/auth/complete`, `/courses`, `/courses/[id]`, `/sessions/[id]`.
- Server actions in `apps/web/lib/auth.ts` set the access cookie server-side for `/login` and `/register`, then redirect directly to `/courses`; `/auth/complete` remains the browser handoff path.
- Protected course/session flows are under `/courses`, `/courses/[id]`, `/sessions/[id]`, with fetch/auth helpers in `apps/web/lib/api.ts` and `apps/web/lib/courseApi.ts`.
- E2E tests rely on explicit URL waits for auth/navigation transitions; fast assertions alone have been flaky under full verification.