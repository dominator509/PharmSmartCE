# OBSERVABILITY.md

## Logging Strategy
- Library: `structlog`. JSON in non-local envs; console renderer locally.
- Required context fields (bound in middleware): `request_id`, `user_id`,
  `org_id`, `route`, `method`, `status`, `duration_ms`, `app_env`,
  `image_sha`.
- Service-level events use named loggers (`generation`, `ingest`, `auth`)
  and add domain context: `course_id`, `session_id`, `source_id`,
  `llm_provider`, `llm_input_tokens`, `llm_output_tokens`, `citation_overlap`.
- `request_id` is a ULID generated in middleware and returned in
  `X-Request-Id`.

## Redaction
See `SECURITY.md`. Implementation in
`apps/api/app/observability/logging.py::RedactProcessor`.

## Metrics (Prometheus at `GET /metrics`)
| Metric | Type | Labels | Description |
|---|---|---|---|
| `http_request_duration_seconds` | histogram | `method`, `route`, `status` | Request latency |
| `http_requests_total` | counter | `method`, `route`, `status` | Count |
| `llm_generation_duration_seconds` | histogram | `provider` | LLM call latency |
| `llm_tokens_total` | counter | `provider`, `direction` ∈ {input,output} | Token usage |
| `openai_cost_usd_total` | counter | (none) | Monotonic USD spend |
| `openai_cost_usd_monthly` | gauge | `year_month` | Current month spend |
| `openai_cap_warn_80_total` | counter | (none) | Monthly spend reached 80% of cap |
| `openai_cap_reached_total` | counter | (none) | Monthly spend reached cap |
| `question_grounding_failures_total` | counter | `reason` ∈ {overlap_low,refused,retry_exhausted,injection_flagged} | Failures |
| `citation_overlap_ratio` | histogram | (none) | Overlap distribution on accepted Qs |
| `generation_retries_total` | counter | `outcome` ∈ {success,exhausted} | Retries |
| `ingest_duration_seconds` | histogram | `stage` ∈ {extract,chunk,embed,index} | Stage timing |
| `ingest_jobs_total` | counter | `outcome` ∈ {success,failure} | Jobs |
| `faiss_index_size_bytes` | gauge | `course_id` | Index size |
| `background_queue_depth` | gauge | `queue` ∈ {ingest,generation,eval} | Pending jobs |
| `auth_login_attempts_total` | counter | `outcome` ∈ {success,bad_password,rate_limited,unknown_user} | Logins |

## Traces
Optional. When `OTEL_EXPORTER_OTLP_ENDPOINT` is set, OTel exports spans for
HTTP requests, service methods, LLM calls, repo calls. Off by default for cost.

## Health Checks
See `OPERATIONS.md`.

## Dashboards
1. **API Latency** — P50/95/99 of `http_request_duration_seconds` per route;
   request rate; error rate.
2. **Generation Health** — `llm_generation_duration_seconds` P95;
   `question_grounding_failures_total` by `reason`;
   `citation_overlap_ratio` histogram; `generation_retries_total`.
3. **Ingest Pipeline** — `ingest_duration_seconds` by stage; queue depth;
   failures; throughput.
4. **Cost** — `openai_cost_usd_monthly` vs `OPENAI_MONTHLY_USD_CAP`.
5. **Auth** — login attempts by outcome; rate-limit hits.
6. **System** — CPU, memory, disk; FAISS size; pool utilization.

## Alerts
| Name | Condition | Severity | Channel |
|---|---|---|---|
| `api_5xx_high` | 5xx rate > 1% over 5 m | Sev2 | page |
| `api_latency_p95_high` | P95(/api/sessions/start) > 30 s over 10 m | Sev2 | page |
| `grounding_failure_high` | `question_grounding_failures_total` rate > 0.1% over 1 h | Sev1 | page |
| `openai_cap_warn_80` | `openai_cost_usd_monthly >= 0.8 * cap` | Sev3 | email |
| `openai_cap_reached` | `openai_cost_usd_monthly >= cap` | Sev2 | page (auto-fallback) |
| `queue_depth_high` | `background_queue_depth{queue!=eval} > 100` 15 m | Sev3 | email |
| `readyz_failing` | `/readyz` down 2 m | Sev1 | page |
| `auth_brute_force` | `auth_login_attempts_total{outcome="bad_password"} > 100/min` | Sev2 | page |

## SLI / SLO
| SLI | Definition | SLO (90-day) |
|---|---|---|
| API availability | `1 - (5xx + 429) / requests` | 99.5% |
| Generation success | `1 - failed_sessions / total_sessions` | 99.0% |
| Citation accuracy (eval) | golden-set overlap pass rate | ≥ 99% |
| P95 session-start latency | `histogram_quantile(0.95, ...)` on `/api/sessions/*/start` | ≤ 30 s |

## Debugging Production Issues
1. Open the dashboard for the suspect domain.
2. Filter logs by `request_id` from the customer's `X-Request-Id`.
3. Correlate with Sentry issue.
4. Check `/readyz` body for which subsystem is down.
5. Apply the runbook from `OPERATIONS.md`.

## Observability Acceptance Criteria
- [ ] `scripts/smoke-test.sh` produces logs with all required fields.
- [ ] `/metrics` returns all named metrics non-zero after smoke.
- [ ] One alert rule fires in staging during the synthetic fault test in `EP-008`.
- [ ] Sentry shows the synthetic exception during the same test.
