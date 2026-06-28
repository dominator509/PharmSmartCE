from __future__ import annotations

import io
from zipfile import ZIP_DEFLATED, ZipFile

from app.services.generation.service import _normalize_text


def test_normalize_text_extracts_docx_content() -> None:
    content = _build_docx_bytes("Beta blockers reduce heart rate and blood pressure.")

    normalized = _normalize_text(content, "source.docx", "deadbeef")

    assert "Beta blockers reduce heart rate" in normalized


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
