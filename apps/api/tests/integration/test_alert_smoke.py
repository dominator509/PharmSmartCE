from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from app.config import Settings
from app.main import create_app


class FakeAlertProvider:
    def __init__(self) -> None:
        self.alerts: list[str] = []

    def record(self, alert_name: str) -> None:
        self.alerts.append(alert_name)


def test_synthetic_5xx_burst_triggers_alert_provider(tmp_path: Path) -> None:
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
        app.state.alert_provider = FakeAlertProvider()

        @app.get("/boom")
        async def boom() -> None:
            raise RuntimeError("synthetic failure")

        with TestClient(app, raise_server_exceptions=False) as client:
            for _ in range(3):
                response = client.get("/boom")
                assert response.status_code == 500

        assert app.state.alert_provider.alerts
        assert "api_5xx_high" in app.state.alert_provider.alerts
