from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Request latency.",
    ("method", "route", "status"),
)
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Request count.",
    ("method", "route", "status"),
)
LLM_GENERATION_DURATION_SECONDS = Histogram(
    "llm_generation_duration_seconds",
    "LLM call latency.",
    ("provider",),
)
LLM_TOKENS_TOTAL = Counter(
    "llm_tokens_total",
    "Token usage.",
    ("provider", "direction"),
)
OPENAI_COST_USD_TOTAL = Counter(
    "openai_cost_usd_total",
    "Monotonic USD spend.",
)
OPENAI_COST_USD_MONTHLY = Gauge(
    "openai_cost_usd_monthly",
    "Current month spend.",
    ("year_month",),
)
OPENAI_CAP_WARN_80_TOTAL = Counter(
    "openai_cap_warn_80_total",
    "OpenAI monthly spend reached 80 percent of the cap.",
)
OPENAI_CAP_REACHED_TOTAL = Counter(
    "openai_cap_reached_total",
    "OpenAI monthly spend reached the cap.",
)
QUESTION_GROUNDING_FAILURES_TOTAL = Counter(
    "question_grounding_failures_total",
    "Question grounding failures.",
    ("reason",),
)
CITATION_OVERLAP_RATIO = Histogram(
    "citation_overlap_ratio",
    "Overlap distribution on accepted questions.",
)
GENERATION_RETRIES_TOTAL = Counter(
    "generation_retries_total",
    "Generation retries.",
    ("outcome",),
)
INGEST_DURATION_SECONDS = Histogram(
    "ingest_duration_seconds",
    "Ingest timing.",
    ("stage",),
)
INGEST_JOBS_TOTAL = Counter(
    "ingest_jobs_total",
    "Ingest jobs.",
    ("outcome",),
)
FAISS_INDEX_SIZE_BYTES = Gauge(
    "faiss_index_size_bytes",
    "Index size.",
    ("course_id",),
)
BACKGROUND_QUEUE_DEPTH = Gauge(
    "background_queue_depth",
    "Pending jobs.",
    ("queue",),
)
AUTH_LOGIN_ATTEMPTS_TOTAL = Counter(
    "auth_login_attempts_total",
    "Login attempts.",
    ("outcome",),
)

METRIC_NAMES = (
    "http_request_duration_seconds",
    "http_requests_total",
    "llm_generation_duration_seconds",
    "llm_tokens_total",
    "openai_cost_usd_total",
    "openai_cost_usd_monthly",
    "openai_cap_warn_80_total",
    "openai_cap_reached_total",
    "question_grounding_failures_total",
    "citation_overlap_ratio",
    "generation_retries_total",
    "ingest_duration_seconds",
    "ingest_jobs_total",
    "faiss_index_size_bytes",
    "background_queue_depth",
    "auth_login_attempts_total",
)


def record_http_request(method: str, route: str, status: int, duration_seconds: float) -> None:
    status_text = str(status)
    HTTP_REQUEST_DURATION_SECONDS.labels(method=method, route=route, status=status_text).observe(
        duration_seconds
    )
    HTTP_REQUESTS_TOTAL.labels(method=method, route=route, status=status_text).inc()


def record_llm_generation(provider: str, duration_seconds: float) -> None:
    LLM_GENERATION_DURATION_SECONDS.labels(provider=provider).observe(duration_seconds)


def record_llm_tokens(provider: str, direction: str, count: int) -> None:
    LLM_TOKENS_TOTAL.labels(provider=provider, direction=direction).inc(count)


def record_openai_spend(amount: float, year_month: str) -> None:
    OPENAI_COST_USD_TOTAL.inc(amount)
    OPENAI_COST_USD_MONTHLY.labels(year_month=year_month).set(amount)


def set_openai_monthly_spend(year_month: str, amount: float) -> None:
    OPENAI_COST_USD_MONTHLY.labels(year_month=year_month).set(amount)


def record_openai_cap_warn_80() -> None:
    OPENAI_CAP_WARN_80_TOTAL.inc()


def record_openai_cap_reached() -> None:
    OPENAI_CAP_REACHED_TOTAL.inc()


def record_grounding_failure(reason: str) -> None:
    QUESTION_GROUNDING_FAILURES_TOTAL.labels(reason=reason).inc()


def record_generation_retry(outcome: str) -> None:
    GENERATION_RETRIES_TOTAL.labels(outcome=outcome).inc()


def record_citation_overlap(ratio: float) -> None:
    CITATION_OVERLAP_RATIO.observe(ratio)


def record_ingest_duration(stage: str, duration_seconds: float) -> None:
    INGEST_DURATION_SECONDS.labels(stage=stage).observe(duration_seconds)


def record_ingest_job(outcome: str) -> None:
    INGEST_JOBS_TOTAL.labels(outcome=outcome).inc()


def set_faiss_index_size(course_id: str, size_bytes: int) -> None:
    FAISS_INDEX_SIZE_BYTES.labels(course_id=course_id).set(size_bytes)


def set_background_queue_depth(queue: str, depth: int) -> None:
    BACKGROUND_QUEUE_DEPTH.labels(queue=queue).set(depth)


def record_auth_login_attempt(outcome: str) -> None:
    AUTH_LOGIN_ATTEMPTS_TOTAL.labels(outcome=outcome).inc()
