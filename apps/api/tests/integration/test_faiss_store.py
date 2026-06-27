from __future__ import annotations

import numpy as np

from app.adapters.storage.faiss_store import FaissStore


def test_faiss_store_round_trip(tmp_path) -> None:
    store = FaissStore("course-1", tmp_path)
    store.add(
        ["chunk-1", "chunk-2", "chunk-3"],
        np.array([[0.0], [2.0], [5.0]], dtype="float32"),
        [{"page": 1}, {"page": 2}, {"page": 3}],
    )

    assert store.search([1.5], k=2) == [
        ("chunk-2", {"page": 2}),
        ("chunk-1", {"page": 1}),
    ]

    reloaded = FaissStore.load("course-1", tmp_path)
    assert reloaded.search([1.5], k=2) == [
        ("chunk-2", {"page": 2}),
        ("chunk-1", {"page": 1}),
    ]
