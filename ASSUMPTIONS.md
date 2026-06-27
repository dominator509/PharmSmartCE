# Assumptions

Each assumption MUST be reviewed in `EP-000` and `EP-001`. If verification
fails, the responsible ExecPlan records the change in its Decision Log and
updates this file.

| # | Assumption | Reason | Risk if Wrong | How to Verify | Blocks? |
|---|---|---|---|---|---|
| A1 | Backend: Python 3.11 + FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic | Async, strong LLM ecosystem | Rework | EP-001 milestones | No |
| A2 | Frontend: Next.js 14 (App Router) + TS + Tailwind | SSR, free hosting tiers | Rework | EP-005 skeleton | No |
| A3 | DB: PostgreSQL 15 | Cheap managed; JSONB | Migration cost | EP-003 provision | No |
| A4 | LLM: 7–8B GGUF Q4_K_M via `llama-cpp-python`, CPU-only | Required CPU-only | Latency > 60s P95 | EP-002 bench | YES |
| A5 | OpenAI adapter OFF by default; `LLM_PROVIDER=openai` + `OPENAI_MONTHLY_USD_CAP` required | Cost control | Surprise bill | Cap test in EP-006 | No |
| A6 | RAG: FAISS local for v1; pgvector reserved for v2 | Simpler | Scaling ceiling | EP-003 bench | No |
| A7 | Auth: email/password + Argon2id + JWT (15m) + refresh (httpOnly, 30d) | Standard | Standard risks | EP-006 + sec checklist | No |
| A8 | Object storage: S3-compatible (R2/B2) | Cheap egress | Vendor risk (S3 API mitigates) | EP-009 provision | No |
| A9 | Hosting: containers on Fly.io or Render | Budget-friendly | Cold-start | EP-009 smoke | No |
| A10 | CI/CD: GitHub Actions | Free at modest usage | Vendor lock-in | None | No |
| A11 | Package managers: `uv` (Python) + `pnpm` (Node) | Fast, deterministic | Learning curve | EP-001 install.sh | No |
| A12 | "Source of truth" = uploaded docs; LLM MUST refuse outside retrieved chunks | Clinical accuracy goal | Hallucination | Eval harness | YES |
| A13 | Citations: `source_doc_id + source_page + source_span` rendered as hyperlinks | Goal "real hyperlinks" | Credibility | Schema + UI test | YES |
| A14 | Not HIPAA but credentials + uploads encrypted at rest & in transit | Industry baseline | Compromise | EP-006 + SECURITY.md | No |
| A15 | No formal WCAG target but semantic HTML + keyboard nav baseline | Cheap to add | Future lawsuits if scaled | eslint-plugin-jsx-a11y | No |
| A16 | Observability: structlog + Prometheus + Sentry | Free/cheap tier | Limited tracing | EP-008 | No |
| A17 | Generation worker: async queue (Redis+RQ or FastAPI BackgroundTasks v1) | CPU LLM slow | Worker mgmt | EP-004 perf | No |
| A18 | Embeddings: sentence-transformers MiniLM CPU-only | Free, small, fast | Quality ceiling | EP-003 eval | No |
