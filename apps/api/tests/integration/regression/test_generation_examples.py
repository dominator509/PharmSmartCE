from __future__ import annotations

import json

from app.domain.entities import Chunk
from app.services.generation.citation_validator import CitationValidator
from app.services.generation.grounded_llm import GroundedLLM


class LowOverlapLLM:
    def generate(self, prompt: str, max_tokens: int) -> str:
        del prompt, max_tokens
        return json.dumps(
            {
                "stem": "Which statement is best supported?",
                "choices": [
                    "Supported by the source",
                    "Choice B",
                    "Choice C",
                    "Choice D",
                ],
                "correct_choice_index": 0,
                "rationale": "This explanation uses different wording from the source text.",
            }
        )


def test_low_overlap_generation_regression_is_rejected_by_validator() -> None:
    chunk = Chunk(
        doc_id="sample-ce",
        page=1,
        span="p1:s1",
        text="Beta blockers reduce heart rate and blood pressure.",
    )

    question = GroundedLLM(llm=LowOverlapLLM()).generate_question(chunk)

    assert CitationValidator().validate(question, chunk) is False
