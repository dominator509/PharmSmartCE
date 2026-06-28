# ROLLBACK.md

## Triggers
- 5xx rate > 1% sustained 10 minutes on prod.
- P95 latency on `/api/sessions/*/start` > 2× baseline for 10 minutes.
- `question_grounding_failures_total` rate > 0.5% for 15 minutes.
- Any data-corruption indicator (duplicate PKs, FK violations in logs).
- Sev1 Sentry issue specific to the new release.

## Decision Owner
On-call engineer initiates. Backup on-call (or maintainer) acknowledges
within 5 minutes — acknowledgement, not approval. If no ack in 5 min,
proceed and document.

## Rollback Types
| Type | When | Mechanism |
|---|---|---|
| Application image | Code defect | `flyctl releases rollback` |
| Configuration | Bad env var | `flyctl secrets set/unset` + redeploy |
| Database | Bad migration | Forward-fix preferred; reverse only if migration tagged reversible |
| Feature flag / env toggle | Bad behavior gated by env var | Flip env var and redeploy |

## Application Rollback Steps
```sh
flyctl releases --app pharmsmartce-api-prod
flyctl releases rollback <version> --app pharmsmartce-api-prod
flyctl releases rollback <version> --app pharmsmartce-web-prod
```
Verify `/healthz` and `/readyz`. Run
`scripts/smoke-test.sh https://app.pharmsmartce.com`.

## Database Rollback
- **Default: forward-fix.** Create a remediation migration that reverses the
  problem and ship as a normal release.
- **Only if** the broken migration was `# reversible: yes` AND no new data
  depends on it:
  ```sh
  flyctl ssh console --app pharmsmartce-api-prod \
    --command "alembic downgrade -1"
  ```
  Still sensitive — treat as S6 unless a human approved.

## Config Rollback
```sh
flyctl secrets unset BAD_VAR --app pharmsmartce-api-prod
flyctl secrets set BAD_VAR=good_value --app pharmsmartce-api-prod
flyctl deploy --image <current_image> --app pharmsmartce-api-prod
```

## Feature Flag Rollback
At launch, feature toggles are env vars. Disable a feature:
```sh
flyctl secrets set FEATURE_X_ENABLED=false --app pharmsmartce-api-prod
```
Triggers a redeploy.

## Verification After Rollback
- [ ] `/healthz` and `/readyz` 200.
- [ ] `scripts/smoke-test.sh` passes.
- [ ] Error and grounding-failure dashboards return to baseline in 15 min.
- [ ] Customer-impact tickets updated.

## Communication
```
[Status] PharmSmartCE — rollback at HH:MM UTC

We detected <issue> after release vX.Y.Z. We rolled back to vX.Y.(Z-1) at
HH:MM UTC. Service has returned to normal. We are investigating root cause.
Next update at HH:MM UTC.
```

## Postmortem
Blameless postmortem within 5 business days for any Sev1/Sev2 rollback.
Template: `.agent/templates/runbook-template.md` (Postmortem section).

## Evidence Ledger
Record each actual drill in `PRODUCTION_EVIDENCE.md` with the date,
version/commit, and verification outcome.
