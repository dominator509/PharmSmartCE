import pytest

from app.domain.entities import Chunk
from app.domain.errors import DomainError


def test_chunk_accepts_valid_values() -> None:
    chunk = Chunk(doc_id="doc-1", page=1, span="p1:s1", text="Alpha beta gamma.")

    assert chunk.doc_id == "doc-1"
    assert chunk.page == 1
    assert chunk.span == "p1:s1"


@pytest.mark.parametrize(
    "field_name, value",
    [
        ("doc_id", "   "),
        ("page", 0),
        ("span", "   "),
        ("text", "   "),
    ],
)
def test_chunk_rejects_blank_or_invalid_core_fields(field_name: str, value: object) -> None:
    kwargs = {"doc_id": "doc-1", "page": 1, "span": "p1:s1", "text": "Alpha beta gamma."}
    kwargs[field_name] = value

    with pytest.raises(DomainError):
        Chunk(**kwargs)
