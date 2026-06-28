from __future__ import annotations

import json
from pathlib import Path

from app.adapters.llm.fake_adapter import FakeLLM
from app.domain.entities import Chunk
from app.services.generation.citation_validator import CitationValidator, compute_overlap
from app.services.generation.grounded_llm import GroundedLLM


def test_generation_golden_set_meets_accuracy_and_uniqueness_thresholds() -> None:
    rows = _load_rows()
    grounded_llm = GroundedLLM(llm=FakeLLM())
    validator = CitationValidator()

    questions = []
    valid_count = 0

    for index, row in enumerate(rows, start=1):
        chunk = Chunk(
            doc_id=row["source"],
            page=index,
            span=f"p{index}:s1-s{len(row['prompt_chunk'])}",
            text=row["prompt_chunk"],
        )
        question = grounded_llm.generate_question(chunk)
        questions.append(question)
        if validator.validate(question, chunk):
            valid_count += 1
        assert compute_overlap(question.rationale, row["expected_overlap_passage"]) >= 0.4

    accuracy = valid_count / len(rows)
    uniqueness = len({question.stem for question in questions}) / len(questions)

    assert accuracy >= 0.99
    assert uniqueness >= 0.95


def _load_rows() -> list[dict[str, str]]:
    golden_path = Path(__file__).resolve().parents[1] / "fixtures" / "golden_set.jsonl"
    lines = golden_path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line]
