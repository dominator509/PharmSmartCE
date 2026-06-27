# Checklist: Validation

Run these in order. Each should print its `: ok` line.

- [ ] `scripts/preflight.sh` → `preflight: ok`
- [ ] `scripts/lint.sh` → `lint: ok`
- [ ] `scripts/format-check.sh` → `format check: ok`
- [ ] `scripts/typecheck.sh` → `typecheck: ok`
- [ ] `scripts/test-unit.sh` → `unit tests: ok`
- [ ] `scripts/test-integration.sh` → `integration tests: ok`
- [ ] `scripts/test-e2e.sh` → `e2e tests: ok`
- [ ] `scripts/build.sh` → `build: ok`
- [ ] `scripts/security-check.sh` → `security check: ok`
- [ ] `scripts/dependency-audit.sh` → `dependency audit: ok`
- [ ] `scripts/smoke-test.sh` → `smoke test: ok`
- [ ] `scripts/verify.sh` → `verify: ok`
