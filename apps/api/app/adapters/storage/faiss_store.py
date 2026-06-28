from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path

import faiss
import numpy as np


class FaissStore:
    def __init__(
        self,
        course_id: str,
        directory: str | Path,
        index: faiss.Index | None = None,
        chunk_ids: Sequence[str] | None = None,
        metadata: Sequence[Mapping[str, object]] | None = None,
    ) -> None:
        self.course_id = course_id
        self.directory = Path(directory)
        self._index = index
        self._chunk_ids = list(chunk_ids or [])
        self._metadata = [dict(item) for item in metadata or []]

    @property
    def index_path(self) -> Path:
        return self.directory / f"{self.course_id}.index"

    @property
    def metadata_path(self) -> Path:
        return self.directory / f"{self.course_id}.meta.jsonl"

    def add(
        self,
        chunk_ids: Sequence[str],
        vectors: Sequence[Sequence[float]] | np.ndarray,
        metadata: Sequence[Mapping[str, object]],
    ) -> None:
        if len(chunk_ids) != len(metadata):
            raise ValueError("chunk_ids and metadata must have the same length.")

        array = np.asarray(vectors, dtype="float32")
        if array.ndim == 1:
            array = array.reshape(1, -1)
        if array.ndim != 2:
            raise ValueError("vectors must be a 2D array.")
        if len(chunk_ids) != array.shape[0]:
            raise ValueError("chunk_ids and vectors must have the same length.")

        self.directory.mkdir(parents=True, exist_ok=True)
        if self._index is None:
            self._index = faiss.IndexFlatL2(array.shape[1])
        elif self._index.d != array.shape[1]:
            raise ValueError("vectors must match the existing index dimension.")

        self._index.add(array)
        self._chunk_ids.extend(chunk_ids)
        self._metadata.extend(dict(item) for item in metadata)

        faiss.write_index(self._index, str(self.index_path))
        with self.metadata_path.open("a", encoding="utf-8") as handle:
            for chunk_id, item in zip(chunk_ids, metadata, strict=True):
                handle.write(
                    json.dumps(
                        {"chunk_id": chunk_id, "metadata": dict(item)},
                        separators=(",", ":"),
                    )
                    + "\n"
                )

    def reset(self) -> None:
        self._index = None
        self._chunk_ids.clear()
        self._metadata.clear()
        if self.index_path.exists():
            self.index_path.unlink()
        if self.metadata_path.exists():
            self.metadata_path.unlink()

    def search(
        self,
        vector: Sequence[float] | np.ndarray,
        k: int,
    ) -> list[tuple[str, dict[str, object]]]:
        if self._index is None:
            raise ValueError("index has not been loaded yet.")

        query = np.asarray(vector, dtype="float32")
        if query.ndim == 1:
            query = query.reshape(1, -1)
        if query.ndim != 2:
            raise ValueError("vector must be one dimensional or a single row.")

        distances, indices = self._index.search(query, k)
        _ = distances
        hits: list[tuple[str, dict[str, object]]] = []
        for index in indices[0]:
            if index < 0:
                continue
            hits.append((self._chunk_ids[index], dict(self._metadata[index])))
        return hits

    @classmethod
    def load(cls, course_id: str, directory: str | Path) -> FaissStore:
        directory_path = Path(directory)
        index_path = directory_path / f"{course_id}.index"
        metadata_path = directory_path / f"{course_id}.meta.jsonl"

        index = faiss.read_index(str(index_path))
        chunk_ids: list[str] = []
        metadata: list[dict[str, object]] = []
        if metadata_path.exists():
            with metadata_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    payload = json.loads(line)
                    chunk_ids.append(str(payload["chunk_id"]))
                    metadata.append(dict(payload["metadata"]))

        if index.ntotal != len(chunk_ids):
            raise ValueError("index and metadata are out of sync.")

        return cls(
            course_id=course_id,
            directory=directory_path,
            index=index,
            chunk_ids=chunk_ids,
            metadata=metadata,
        )
