# frontend/core

- Root is `apps/web`; it is a Next.js App Router app with TypeScript, Tailwind, Vitest, and Playwright.
- Package manifest pins Next.js 15.5.18, React 18.3.1, React DOM 18.3.1, TypeScript 5.6.3, Tailwind 3.4.14, Vitest 2.1.4, Playwright 1.61.1, Prettier 3.3.3, ESLint 8.57.1.
- Scripts in `apps/web/package.json`: `dev`, `build`, `start`, `lint`, `format:check`, `typecheck`, `test:unit`, `test:e2e`.
- `pnpm --filter web test:e2e` runs `apps/web/scripts/run-e2e.mjs`; `packages/shared` is the planned home for generated OpenAPI types.
- State rule stays: server is source of truth for sessions/questions/grading; client cache is React Query only; no durable client-side question persistence beyond ephemeral cache.
- Important planned UX still includes auth pages, course list/detail with source status badges, upload controls for admins, session polling, citation UI, and results/CE record flows.