# Checklist: Release

- [ ] RC criteria met (target PRs merged; `main` CI green; `CHANGELOG [Unreleased]` reflects changes; staging smoke < 24 h)
- [ ] Version bumped in `CHANGELOG.md` and `apps/api/app/__version__.py`
- [ ] Release PR merged with required reviews
- [ ] Tag `vX.Y.Z` pushed
- [ ] `release.yml` staging deploy + smoke green
- [ ] Production environment approval triggered and approved by human (agents: STOP S6)
- [ ] Prod deploy completed + post-deploy smoke green
- [ ] Dashboards watched for 30 min post-deploy with no Sev1/Sev2
- [ ] Release notes posted from `CHANGELOG.md`
- [ ] Evidence captured in `PRODUCTION_EVIDENCE.md`
