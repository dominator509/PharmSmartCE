from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from app.config import Settings
from app.main import create_app
from app.observability.metrics import METRIC_NAMES


def test_metrics_shape_exposes_all_named_metrics(tmp_path: Path) -> None:
    with PostgresContainer(
        image="postgres:15-alpine",
        username="app",
        password="app",
        dbname="pharm",
        driver="asyncpg",
    ) as postgres:
        app = create_app(
            Settings(
                app_env="test",
                database_url=postgres.get_connection_url(),
                storage_root=str(tmp_path / "uploads"),
                faiss_index_dir=str(tmp_path / "faiss"),
            )
        )
        with TestClient(app, base_url="https://testserver") as client:
            client.get("/healthz")
            metrics = client.get("/metrics")

            assert metrics.status_code == 200
            for name in METRIC_NAMES:
                assert name in metrics.text
