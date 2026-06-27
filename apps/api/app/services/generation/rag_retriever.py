from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from app.domain.entities import Chunk, Course


@dataclass(slots=True)
class RAGRetriever:
    chunk_source: Callable[[Course], Sequence[Chunk]]

    def retrieve(self, course: Course, n: int, seed: str) -> list[Chunk]:
        if n <= 0:
            return []

        chunks = list(self.chunk_source(course))
        random.Random(seed).shuffle(chunks)
        distinct_chunks = list(dict.fromkeys(chunks))
        return distinct_chunks[:n]
