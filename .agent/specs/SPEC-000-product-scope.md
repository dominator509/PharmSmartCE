# SPEC-000 — Product Scope

**Status:** Accepted
**Owner:** founding-eng
**Date:** 2026-01
**Linked Roadmap Phase:** P0
**Linked ExecPlans:** EP-000, EP-001

## User-Visible Goal
Pharmacists complete CE modules whose questions are generated dynamically per
session, grounded only in the course's uploaded source material, with every
question carrying a clickable citation hyperlink to the cited passage.

## Non-Goals
- HIPAA-regulated PHI workflows.
- Real-time multi-user collaboration on a single session.
- Mobile native apps.
- Formal ACPE accreditation integration at launch.
- LLM fine-tuning.
- Live proctoring.

## Terms
- **Org** — tenant (pharmacy chain or CE provider).
- **User** — authenticated pharmacist or author.
- **Course** — CE module owned by an Org.
- **Source Document** — uploaded PDF/DOCX; sole source of truth for a course.
- **Chunk** — token-sized portion of a Source Document indexed in FAISS.
- **Question** — generated MCQ tied to a Chunk via citation fields.
- **Session** — one user's attempt at a Course; contains N Questions.
- **Answer** — a user's choice; correctness derived from generation.
- **CE Record** — PDF artifact issued upon passing a Session.
- **Citation** — `source_doc_id + source_page + source_span` rendered as a
  clickable hyperlink.
- **Grounding** — the property that an answer is supported by the cited Chunk.

## Required Behaviors
1. Authors authenticate, create Courses, upload Sources.
2. Ingest worker processes Sources into Chunks + embeddings + FAISS index.
3. Test takers authenticate, list Courses, start a Session.
4. Session start triggers RAG retrieval (deterministic seed = user_id +
   session_id) and per-Chunk Question generation through `grounded_llm`.
5. Citation Validator rejects misaligned generations; retries up to
   `GENERATION_RETRY_BUDGET` per slot.
6. Persisted Questions enforce non-null citation fields.
7. User answers; correctness recorded; score computed; on pass, CE Record
   issued.
8. UI renders citations as inline `[1]` hyperlinks; clicking opens a viewer
   highlighting the cited passage.

## Success Metrics
- Citation accuracy ≥ 99% (golden-set eval).
- Question uniqueness ≥ 95% (Jaccard < 0.5 across two sessions for same
  user+course).
- P95 session-start latency ≤ 30 s.
- Zero ungrounded persisted Questions (NOT NULL + service invariant).
- Launch infra ≤ $100/month.

## Required Tests
- E2E happy path.
- Golden-set citation accuracy + uniqueness.

## Acceptance Criteria
- [ ] Playwright `tests/e2e/happy_path.spec.ts` green.
- [ ] Golden-set eval ≥ 99% citation accuracy, ≥ 95% uniqueness.
- [ ] `scripts/verify.sh` green.
