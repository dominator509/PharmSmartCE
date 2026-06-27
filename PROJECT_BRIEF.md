# PharmSmartCE — Project Brief

## Project Name
PharmSmartCE

## Problem Statement
Pharmacist Continuing Education (CE) is typically delivered with a fixed
question bank. Test takers can memorize, share, or look up answers. There is
no widely available CE platform that generates dynamic per-user test
questions grounded only in the CE material itself, with inline source
citations verifiable by hyperlink.

## Target Users
- Clinical pharmacists (primary)
- Retail/community pharmacists (primary)
- CE course authors (secondary — they upload source material)

## Primary User Outcomes
1. Authors upload a CE source document. It is ingested as the sole source of
   truth for that course.
2. Pharmacists launch a CE module and receive uniquely generated questions
   per session, drawn only from the ingested material.
3. Every question and rationale includes inline citations with verifiable
   hyperlinks back to a specific passage / page of the source.
4. Pharmacists receive a CE completion record after passing.

## Business Goals
- First "smart" pharmacist CE generator with truly dynamic per-session
  questions.
- 100% clinical accuracy — no hallucination beyond source material.
- Cost-effective at launch: CPU-only self-hosted LLM; optional paid fallback
  only if costs remain low.

## Technical Goals
- Self-hosted small LLM (CPU-only via `llama-cpp-python`) is the default.
- Optional OpenAI adapter OFF by default, behind a feature flag and a cost
  cap.
- RAG: every generation prompt includes retrieved passages; the generator
  refuses to answer outside that context.
- Every generated question stores `source_doc_id`, `source_page`,
  `source_span` for hyperlink rendering.

## Out-of-Scope (Non-Goals)
- HIPAA-regulated PHI workflows.
- Real-time multi-user collaboration on a single test session.
- Mobile native apps (responsive web is sufficient at launch).
- Formal ACPE accreditation integration at launch (design accommodates it).
- LLM fine-tuning at launch (RAG only).
- Live proctoring / webcam monitoring.

## Success Metrics
- Citation accuracy ≥ 99% on held-out eval set.
- Question uniqueness ≥ 95% across two sessions for same user/course.
- P95 question-set generation latency ≤ 30 s on 4 vCPU / 8 GB host with 7–8B
  GGUF Q4_K_M.
- Zero ungrounded answers (NOT NULL DB constraint + service invariant).
- Launch infra cost ≤ $100/month.

## Production Readiness Definition
Production-ready when ALL items in `PRODUCTION_READINESS.md` are satisfied:
`scripts/verify.sh` passes, `scripts/production-readiness-check.sh` passes,
staging deploy + rollback drill complete, dashboards show signal for the
synthetic smoke test, secrets live in the deploy platform's secret store,
eval harness hits citation/uniqueness thresholds.
