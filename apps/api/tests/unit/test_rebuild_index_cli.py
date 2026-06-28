from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.cli import rebuild_index


@dataclass(slots=True)
class FakeStore:
    course_id: str
    index_dir: Path
    reset_calls: int = 0
    add_calls: int = 0
    added_chunk_ids: list[str] | None = None
    added_vectors: list[list[float]] | None = None
    added_metadata: list[dict[str, object]] | None = None

    def reset(self) -> None:
        self.reset_calls += 1

    def add(
        self,
        chunk_ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict[str, object]],
    ) -> None:
        self.add_calls += 1
        self.added_chunk_ids = list(chunk_ids)
        self.added_vectors = [list(vector) for vector in vectors]
        self.added_metadata = [dict(item) for item in metadata]


def test_main_requires_all_flag(monkeypatch) -> None:
    called: list[object] = []

    def fake_run(coro) -> None:
        called.append(coro)
        coro.close()

    monkeypatch.setattr(rebuild_index.asyncio, "run", fake_run)

    assert rebuild_index.main(["--all"]) == 0
    assert len(called) == 1


def test_rebuild_course_index_writes_vectors_and_metadata(monkeypatch, tmp_path) -> None:
    fake_store = FakeStore("course-1", tmp_path)
    monkeypatch.setattr(rebuild_index, "FaissStore", lambda course_id, index_dir: fake_store)

    count = rebuild_index._rebuild_course_index(
        "course-1",
        [
            rebuild_index.ChunkRow("chunk-1", "source-1", 1, 0, 12, "Alpha beta"),
            rebuild_index.ChunkRow("chunk-2", "source-1", 2, 13, 29, "Gamma delta"),
        ],
        tmp_path,
    )

    assert count == 2
    assert fake_store.reset_calls == 1
    assert fake_store.add_calls == 1
    assert fake_store.added_chunk_ids == ["chunk-1", "chunk-2"]
    assert fake_store.added_metadata == [
        {
            "source_id": "source-1",
            "page": 1,
            "span_start": 0,
            "span_end": 12,
            "text": "Alpha beta",
        },
        {
            "source_id": "source-1",
            "page": 2,
            "span_start": 13,
            "span_end": 29,
            "text": "Gamma delta",
        },
    ]
    assert len(fake_store.added_vectors or []) == 2
    assert fake_store.added_vectors[0] != fake_store.added_vectors[1]


def test_embed_texts_is_deterministic() -> None:
    first = rebuild_index._embed_texts(["alpha", "beta"])
    second = rebuild_index._embed_texts(["alpha", "beta"])

    assert first == second
    assert len(first) == 2
    assert len(first[0]) == 8
