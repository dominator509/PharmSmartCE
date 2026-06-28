from __future__ import annotations

import io
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from app.services.generation.service import _normalize_text as _normalize_generation_text
from app.services.ingest.service import _normalize_text as _normalize_ingest_text


@pytest.mark.parametrize(
    "normalize_text",
    [_normalize_generation_text, _normalize_ingest_text],
)
def test_normalize_text_extracts_docx_content(normalize_text) -> None:
    content = _build_docx_bytes("Beta blockers reduce heart rate and blood pressure.")

    normalized = normalize_text(content, "source.docx", "deadbeef")

    assert "Beta blockers reduce heart rate" in normalized


@pytest.mark.parametrize(
    "normalize_text",
    [_normalize_generation_text, _normalize_ingest_text],
)
def test_normalize_text_falls_back_for_malformed_docx(normalize_text) -> None:
    normalized = normalize_text(b"not a docx archive", "source.docx", "deadbeef")

    assert normalized == "source.docx deadbeef"


def _build_docx_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr(
            "word/document.xml",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body><w:p><w:r><w:t>"
                f"{text}"
                "</w:t></w:r></w:p></w:body></w:document>"
            ),
        )
    return buffer.getvalue()
