import hashlib

import pytest

from app.adapters.llm.fake_adapter import FakeLLM
from app.domain.entities import Chunk
from app.domain.errors import GroundingError, InsufficientContextError
from app.services.generation.grounded_llm import INSUFFICIENT_CONTEXT_MARKER, GroundedLLM


def test_fake_llm_deterministic() -> None:
    llm = FakeLLM()
    prompt = (
        '<<<context_start id="doc-1:1:a">>>\n'
        "The kidneys filter blood and remove waste.\n"
        "<<<context_end>>>"
    )
    result_a = llm.generate(prompt=prompt, max_tokens=128)
    result_b = llm.generate(prompt=prompt, max_tokens=128)
    result_c = llm.generate(prompt=prompt + " extra", max_tokens=128)

    assert result_a == result_b
    assert result_a != result_c
    assert hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16] in result_a


def test_fake_llm_refuses_without_context_delimiters() -> None:
    llm = FakeLLM()

    assert llm.generate(prompt="No context here.", max_tokens=128) == INSUFFICIENT_CONTEXT_MARKER


def test_fake_llm_refuses_when_context_block_is_malformed() -> None:
    llm = FakeLLM()
    prompt = (
        '<<<context_start id="doc-1:1:a" >>\n'
        "The kidneys filter blood and remove waste.\n"
        "<<<context_end>>>"
    )

    assert llm.generate(prompt=prompt, max_tokens=128) == INSUFFICIENT_CONTEXT_MARKER


def test_grounded_llm_generates_question_from_context() -> None:
    grounded_llm = GroundedLLM(llm=FakeLLM())
    chunk = Chunk(
        doc_id="doc-1",
        page=4,
        span="p4:s2",
        text="Beta blockers reduce heart rate and blood pressure.",
    )

    question = grounded_llm.generate_question(chunk)

    assert question.source_doc_id == "doc-1"
    assert question.source_page == 4
    assert question.source_span == "p4:s2"
    assert question.choices[question.correct_choice_index].startswith("Supported by the source:")


def test_grounded_llm_raises_when_model_refuses() -> None:
    class RefusingLLM:
        def generate(self, prompt: str, max_tokens: int) -> str:
            del prompt, max_tokens
            return INSUFFICIENT_CONTEXT_MARKER

    grounded_llm = GroundedLLM(llm=RefusingLLM())
    chunk = Chunk(doc_id="doc-1", page=4, span="p4:s2", text="Beta blockers reduce heart rate.")

    with pytest.raises(InsufficientContextError):
        grounded_llm.generate_question(chunk)


def test_grounded_llm_rejects_malformed_json() -> None:
    class MalformedLLM:
        def generate(self, prompt: str, max_tokens: int) -> str:
            del prompt, max_tokens
            return "not-json"

    grounded_llm = GroundedLLM(llm=MalformedLLM())
    chunk = Chunk(doc_id="doc-1", page=4, span="p4:s2", text="Beta blockers reduce heart rate.")

    with pytest.raises(GroundingError):
        grounded_llm.generate_question(chunk)


def test_grounded_llm_rejects_non_mapping_payload() -> None:
    class NonMappingLLM:
        def generate(self, prompt: str, max_tokens: int) -> str:
            del prompt, max_tokens
            return "[]"

    grounded_llm = GroundedLLM(llm=NonMappingLLM())
    chunk = Chunk(doc_id="doc-1", page=4, span="p4:s2", text="Beta blockers reduce heart rate.")

    with pytest.raises(GroundingError):
        grounded_llm.generate_question(chunk)


@pytest.mark.parametrize(
    "payload",
    [
        ('{"stem": "", "choices": ["A"], ' '"correct_choice_index": 0, "rationale": "ok"}'),
        ('{"stem": "ok", "choices": [], ' '"correct_choice_index": 0, "rationale": "ok"}'),
        ('{"stem": "ok", "choices": ["A"], ' '"correct_choice_index": "0", "rationale": "ok"}'),
        ('{"stem": "ok", "choices": ["A"], ' '"correct_choice_index": true, "rationale": "ok"}'),
        ('{"stem": "ok", "choices": ["A"], ' '"correct_choice_index": 1, "rationale": "ok"}'),
        ('{"stem": "ok", "choices": ["A"], ' '"correct_choice_index": 0, "rationale": ""}'),
    ],
)
def test_grounded_llm_rejects_invalid_question_fields(payload: str) -> None:
    class InvalidFieldLLM:
        def generate(self, prompt: str, max_tokens: int) -> str:
            del prompt, max_tokens
            return payload

    grounded_llm = GroundedLLM(llm=InvalidFieldLLM())
    chunk = Chunk(doc_id="doc-1", page=4, span="p4:s2", text="Beta blockers reduce heart rate.")

    with pytest.raises(GroundingError):
        grounded_llm.generate_question(chunk)
