from __future__ import annotations

import json
from dataclasses import dataclass

from app.domain.entities import Chunk, Question
from app.domain.errors import DomainError, GroundingError, InsufficientContextError
from app.services.ports.llm import LLMPort

INSUFFICIENT_CONTEXT_MARKER = "<<<INSUFFICIENT_CONTEXT>>>"
SYSTEM_PROMPT = (
    "You are PharmSmartCE. Generate one multiple-choice question only from the "
    "provided context. Never use outside knowledge. Return strict JSON with "
    "keys stem, choices, correct_choice_index, rationale."
)


@dataclass(slots=True)
class GroundedLLM:
    llm: LLMPort
    max_tokens: int = 256

    def generate_question(self, chunk: Chunk) -> Question:
        prompt = self._build_prompt(chunk)
        raw = self.llm.generate(prompt=prompt, max_tokens=self.max_tokens)
        if raw.strip() == INSUFFICIENT_CONTEXT_MARKER:
            raise InsufficientContextError("LLM refused to answer from supplied context.")
        return self._parse_question(raw, chunk)

    def _build_prompt(self, chunk: Chunk) -> str:
        context_id = f"{chunk.doc_id}:{chunk.page}:{chunk.span}".replace('"', '\\"')
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f'<<<context_start id="{context_id}">>>\n'
            f"{chunk.text}\n"
            "<<<context_end>>>\n\n"
            "Return strict JSON only."
        )

    def _parse_question(self, raw: str, chunk: Chunk) -> Question:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GroundingError("LLM returned invalid question payload.") from exc

        if not isinstance(payload, dict):
            raise GroundingError("LLM returned invalid question payload.")

        stem = payload.get("stem")
        choices = payload.get("choices")
        correct_choice_index = payload.get("correct_choice_index")
        rationale = payload.get("rationale")

        if not isinstance(stem, str) or not stem.strip():
            raise GroundingError("LLM returned invalid question payload.")
        if (
            not isinstance(choices, list)
            or not choices
            or not all(isinstance(choice, str) and choice.strip() for choice in choices)
        ):
            raise GroundingError("LLM returned invalid question payload.")
        if not isinstance(correct_choice_index, int) or isinstance(correct_choice_index, bool):
            raise GroundingError("LLM returned invalid question payload.")
        if not isinstance(rationale, str) or not rationale.strip():
            raise GroundingError("LLM returned invalid question payload.")

        try:
            return Question(
                stem=stem,
                choices=tuple(choices),
                correct_choice_index=correct_choice_index,
                rationale=rationale,
                source_doc_id=chunk.doc_id,
                source_page=chunk.page,
                source_span=chunk.span,
            )
        except DomainError as exc:
            raise GroundingError("LLM returned invalid question payload.") from exc
