from __future__ import annotations

import re

from app.domain.entities import Chunk, Question

CITATION_MIN_OVERLAP_RATIO = 0.4


class CitationValidator:
    def validate(
        self,
        question: Question,
        chunk: Chunk,
        min_overlap_ratio: float = CITATION_MIN_OVERLAP_RATIO,
    ) -> bool:
        overlap = compute_overlap(question.rationale, chunk.text)
        return overlap >= min_overlap_ratio


def compute_overlap(rationale: str, chunk_text: str) -> float:
    rationale_tokens = set(_tokenize(rationale))
    if not rationale_tokens:
        return 0.0
    chunk_tokens = set(_tokenize(chunk_text))
    return len(rationale_tokens & chunk_tokens) / len(rationale_tokens)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())
