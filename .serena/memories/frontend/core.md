# frontend/core

- Intended root: `apps/web` (currently absent in blueprint checkout).
- Planned stack: Next.js 14 App Router, TypeScript, React Query, Tailwind; shared OpenAPI-generated TS types expected in `packages/shared`.
- State rule: server is source of truth for sessions/questions/grading; client cache is React Query only; no durable client-side question persistence beyond ephemeral cache.
- Important planned UX: auth pages, course list/detail with source status badges, upload controls for admins, session page polling until ready, MCQ QuestionView, citation superscript + CitationDrawer/deep link, results page + CE record download.
- Frontend validations documented in `COMMANDS.md`: `pnpm --filter web lint`, `format:check`, `typecheck`, `test:unit`, `test:e2e`, `build`; use scripts when milestone says so.