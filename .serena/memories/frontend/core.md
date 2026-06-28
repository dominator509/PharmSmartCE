# frontend/core
- Root is `apps/web`; it is a Next.js App Router app with TypeScript, Tailwind, Vitest, and Playwright.
- Scripts in `apps/web/package.json`: `dev`, `build`, `start`, `lint`, `format:check`, `typecheck`, `test:unit`, `test:e2e`.
- `pnpm --filter web test:e2e` runs `apps/web/scripts/run-e2e.mjs`; generated OpenAPI types are planned for `packages/shared`.
- Session state stays server-owned; the client cache is React Query only, and there is no durable client-side question persistence beyond ephemeral cache.
- Important UX surfaces still include auth pages, course list/detail with source status badges, admin upload controls, session polling, citation UI, and results/CE record flows.