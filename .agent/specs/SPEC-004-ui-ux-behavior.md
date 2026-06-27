# SPEC-004 — UI / UX Behavior

**Status:** Accepted
**Owner:** founding-eng
**Date:** 2026-01
**Linked Roadmap Phase:** P4
**Linked ExecPlans:** EP-005

## User-Visible Goal
A usable, accessible web UI that lets pharmacists complete sessions with
clear citation hyperlinks and lets authors upload sources.

## Non-Goals
- Native mobile app.
- Offline mode.
- Multi-language at launch.

## Screens
| Route | Purpose | States |
|---|---|---|
| `/login` | Email/password login | idle, submitting, error (invalid), error (rate-limited) |
| `/register` | New account | idle, submitting, error (taken), error (validation) |
| `/courses` | Org's courses | loading, empty, error, success |
| `/courses/[id]` | Course detail; author can upload | loading, empty, error, success; upload states (idle, uploading, ingesting, ready, failed, quarantined) |
| `/sessions/[id]` | Take a session | loading (generation), question view, answer feedback, results |
| `/sessions/[id]/results` | Results, CE PDF download | loading, success, error |
| `/account` | Logout, change password | idle, submitting, success, error |

## Citation Rendering
- Within question text and rationale, citations render as a clickable
  superscript `[1]` style.
- Clicking opens a side drawer (`CitationDrawer`) that fetches the source
  passage and highlights the cited span.
- Drawer URL deep-linkable: `/sessions/{id}?cite=<doc_id>:<page>:<span>`.

## Accessibility (Baseline)
- Semantic HTML (`<main>`, `<nav>`, `<button>`).
- Every interactive control keyboard-reachable.
- Focus rings preserved (no `outline: none`).
- aria-labels on icon-only buttons.
- Color contrast ≥ WCAG AA.

## Loading / Empty / Error States
- Skeleton loaders for course list and session generation.
- Empty `/courses` state with admin CTA.
- Form errors inline; network errors as non-blocking toast with retry.
- Server problem+json `detail` shown verbatim when safe.

## Performance
- LCP < 2.5 s on a fast 3G profile for `/login` and `/courses`.
- Session page splits LLM-generated content from chrome so chrome renders
  immediately; skeleton fills the question area until generation finishes.

## Observability
- Send `X-Request-Id` from the client on retries; surface in support tickets.
- Sentry (browser) captures unhandled exceptions; PII redacted.

## Required Tests
- Playwright happy path (`tests/e2e/happy_path.spec.ts`).
- Playwright auth flows.
- Playwright citation drawer deep-link.
- axe-core check on `/login`, `/courses`, `/sessions/:id`.

## Acceptance Criteria
- [ ] Playwright happy path green.
- [ ] axe-core reports no `serious` violations on listed pages.
- [ ] Citation drawer opens for every clicked citation in a smoke run.
