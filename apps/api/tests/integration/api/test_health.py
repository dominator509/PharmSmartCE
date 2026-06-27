from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from app.config import Settings
from app.main import create_app


def test_health_and_readyz_and_metrics(tmp_path: Path) -> None:
    with PostgresContainer(
        image="postgres:15-alpine",
        username="app",
        password="app",
        dbname="pharm",
        driver="asyncpg",
    ) as postgres:
        faiss_dir = tmp_path / "faiss"
        app = create_app(
            Settings(
                database_url=postgres.get_connection_url(),
                faiss_index_dir=str(faiss_dir),
            )
        )
        with TestClient(app) as client:
            health = client.get("/healthz")
            ready = client.get("/readyz")
            metrics = client.get("/metrics")

            assert health.status_code == 200
            assert health.json() == {"status": "ok"}
            assert ready.status_code == 200
            assert ready.json() == {"db": True, "faiss": True, "llm": True}
            assert metrics.status_code == 200
            assert "# HELP" in metrics.text

            client.app.state.llm_ready = False
            not_ready = client.get("/readyz")
            assert not_ready.status_code == 503
            assert not_ready.json() == {"db": True, "faiss": True, "llm": False}
