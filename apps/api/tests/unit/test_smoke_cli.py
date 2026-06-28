from __future__ import annotations

from dataclasses import dataclass

from app.cli import smoke


@dataclass(slots=True)
class FakeResponse:
    status_code: int
    json_data: dict[str, object]
    headers: dict[str, str] | None = None
    text: str = ""

    def json(self) -> dict[str, object]:
        return self.json_data


class FakeClient:
    def __init__(self, base_url: str, timeout: float, follow_redirects: bool) -> None:
        del timeout, follow_redirects
        self.base_url = base_url
        self.cookies: dict[str, str] = {}
        self.logged_out = False
        self.answer_count = 0
        self.questions = [
            {
                "id": f"question-{index}",
                "text": f"Question {index}",
                "options": [
                    "Supported by the source: alpha",
                    "Distractor 1",
                    "Distractor 2",
                    "Distractor 3",
                ],
                "citation": {
                    "doc_id": "doc-1",
                    "page": index,
                    "span": f"p{index}:s1-s5",
                    "url": f"/sessions/session-1?cite=doc-1:{index}:p{index}:s1-s5",
                },
            }
            for index in range(1, 7)
        ]

    def __enter__(self) -> FakeClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        del exc_type, exc, tb

    def get(self, path: str, headers: dict[str, str] | None = None) -> FakeResponse:
        del headers
        if path in {"/healthz", "/readyz"}:
            return FakeResponse(200, {"status": "ok"})
        if path.startswith("/sessions/session-1?cite="):
            return FakeResponse(200, {"status": "ok"})
        if path == "/api/sessions/session-1":
            if self.answer_count >= len(self.questions):
                return FakeResponse(
                    200,
                    {
                        "status": "completed",
                        "questions": self.questions,
                        "record_id": "record-1",
                    },
                )
            return FakeResponse(200, {"status": "in_progress", "questions": self.questions})
        if path == "/api/ce-records/record-1":
            return FakeResponse(
                200,
                {
                    "id": "record-1",
                    "session_id": "session-1",
                    "pdf_storage_key": "records/session-1.pdf",
                    "issued_at": "2026-06-27T00:00:00Z",
                    "download_url": "/api/ce-records/record-1/download",
                },
            )
        if path == "/api/ce-records/record-1/download":
            return FakeResponse(200, {}, headers={"content-type": "application/pdf"})
        raise AssertionError(f"Unexpected GET {path}")

    def post(
        self,
        path: str,
        json: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
        files: object | None = None,
        cookies: dict[str, str] | None = None,
    ) -> FakeResponse:
        del headers, files, json
        if path == "/auth/register":
            return FakeResponse(201, {"id": "user-1"})
        if path == "/auth/login":
            self.cookies["refresh"] = "refresh-a"
            return FakeResponse(
                200,
                {"access_token": "access-a", "token_type": "Bearer", "expires_in": 900},
            )
        if path == "/auth/refresh":
            if self.logged_out or (
                cookies is not None and cookies.get("refresh") == "refresh-a" and self.logged_out
            ):
                return FakeResponse(401, {"detail": "invalid"})
            self.cookies["refresh"] = "refresh-b"
            return FakeResponse(
                200,
                {"access_token": "access-b", "token_type": "Bearer", "expires_in": 900},
            )
        if path == "/api/courses":
            return FakeResponse(201, {"id": "course-1"})
        if path == "/api/courses/course-1/sources":
            return FakeResponse(202, {"id": "source-1", "status": "uploaded"})
        if path == "/api/sessions/course-1/start":
            return FakeResponse(201, {"id": "session-1"})
        if path == "/api/sessions/session-1/answers":
            self.answer_count += 1
            return FakeResponse(200, {"correct": True})
        if path == "/auth/logout":
            self.logged_out = True
            return FakeResponse(204, {})
        raise AssertionError(f"Unexpected POST {path}")


def test_smoke_main_selects_local_and_remote(monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(smoke, "_run_local_smoke", lambda: calls.append("local"))
    monkeypatch.setattr(smoke, "_run_remote_smoke", lambda base_url: calls.append(base_url))

    assert smoke.main(["http://localhost:8000"]) == 0
    assert smoke.main(["https://staging.example"]) == 0
    assert calls == ["local", "https://staging.example"]


def test_remote_smoke_runs_full_flow(monkeypatch) -> None:
    monkeypatch.setattr(smoke.httpx, "Client", FakeClient)

    smoke._run_remote_smoke("https://staging.example")


def test_supported_choice_index_finds_supported_option() -> None:
    assert smoke._supported_choice_index(["No", "Supported by the source: alpha", "Maybe"]) == 1
