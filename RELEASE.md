# RELEASE.md

## Release Types
- **Major (X.0.0)** — breaking API or data-model changes.
- **Minor (X.Y.0)** — new features, backward compatible.
- **Patch (X.Y.Z)** — bug fixes only.
- **Hotfix (X.Y.Z+1 off main)** — emergency fix; cherry-picked.

## Versioning
SemVer. Git tag `vX.Y.Z` drives the CI release pipeline.

## Changelog
`CHANGELOG.md` follows Keep-A-Changelog. Sections: `Added / Changed /
Deprecated / Removed / Fixed / Security`. Every user-visible PR updates
`[Unreleased]`. On tag, the workflow moves it under `[X.Y.Z] - YYYY-MM-DD`.

## Branch Strategy
Trunk-based. `main` is always releasable. Short-lived branches:
- `feat/<slug>`
- `fix/<slug>`
- `chore/<slug>`
- `ep/EP-NNN-<slug>` (agent-driven ExecPlan work)
- `hotfix/<slug>` (cut from release tag)

## Release Candidate Criteria
- All target PRs merged to `main`.
- CI on `main` green.
- `CHANGELOG.md [Unreleased]` reflects actual changes.
- A staging deploy + smoke succeeded in the last 24 h.

## Release Checklist
1. [ ] Confirm RC criteria above.
2. [ ] Bump version in `CHANGELOG.md` and `apps/api/app/__version__.py`.
3. [ ] Open release PR; merge with required reviews.
4. [ ] Tag `vX.Y.Z` on `main` and push.
5. [ ] `release.yml` builds, pushes, deploys to staging, runs smoke. Verify
       green.
6. [ ] Trigger prod deploy via the `production` environment approval.
       (Agents: STOP S6.)
7. [ ] After prod, run `scripts/smoke-test.sh https://app.pharmsmartce.com`.
8. [ ] Watch dashboards 30 min before closing the release.
9. [ ] Post release notes from changelog to the internal channel.

## Smoke Tests
See `scripts/smoke-test.sh` and `OPERATIONS.md`.

## Approvals
- Code: ≥ 1 maintainer review.
- Prod deploy: explicit `production` environment approval (human only).

## Release Notes Template
```
# vX.Y.Z — YYYY-MM-DD

## Highlights
- (1–3 bullets, plain language)

## Added / Changed / Fixed / Security
(copy from CHANGELOG)

## Operational notes
- Migrations: yes/no (id list)
- New env vars: (list)
- Rollback notes: (image tag to roll back to)
```

## Post-Release Monitoring
24-hour heightened watch. On-call checks dashboards at +15 min, +1 h, +6 h,
+24 h. Any Sev1/Sev2 in the window triggers `ROLLBACK.md`.
