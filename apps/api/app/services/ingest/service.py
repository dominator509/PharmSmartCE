from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from time import perf_counter
from uuid import uuid4
from xml.etree import ElementTree as ET

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.observability.metrics import record_ingest_duration, record_ingest_job
from app.repositories.models.chunks import ChunkModel
from app.repositories.models.sources import SourceModel
from app.services.ports.storage import StoragePort


@dataclass(slots=True)
class IngestService:
    session_factory: async_sessionmaker[AsyncSession]
    storage: StoragePort

    async def enqueue(self, source_id: str) -> None:
        started = perf_counter()
        outcome = "failure"
        try:
            async with self.session_factory() as session:
                source = await session.get(SourceModel, source_id)
                if source is None:
                    return

                content = await self.storage.load_source(
                    source.course_id,
                    source.id,
                    source.filename,
                )
                text = _normalize_text(content, source.filename, source.sha256)
                segments = _build_segments(text, 3)

                for index, segment in enumerate(segments):
                    session.add(
                        ChunkModel(
                            id=uuid4().hex,
                            source_id=source.id,
                            page=index + 1,
                            span_start=0,
                            span_end=len(segment),
                            text=segment,
                            embedding_index=index,
                        )
                    )

                source.status = "ready"
                source.last_error = None
                await session.commit()
                outcome = "success"
        finally:
            record_ingest_job(outcome)
            record_ingest_duration("index", perf_counter() - started)


def _normalize_text(content: bytes, filename: str, sha256_hex: str) -> str:
    is_docx = filename.lower().endswith(".docx")
    if is_docx or zipfile.is_zipfile(io.BytesIO(content)):
        extracted = _extract_docx_text(content)
        if extracted:
            return extracted
        if is_docx:
            return f"{filename} {sha256_hex}"
    text = content.decode("utf-8", errors="ignore")
    normalized = " ".join(text.split()).strip()
    if normalized:
        return normalized
    return f"{filename} {sha256_hex}"


def _extract_docx_text(content: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            document = archive.read("word/document.xml")
    except (KeyError, OSError, zipfile.BadZipFile):
        return ""

    try:
        root = ET.fromstring(document)
    except ET.ParseError:
        return ""

    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    text_nodes = [node.text or "" for node in root.findall(".//w:t", namespace)]
    normalized = " ".join(" ".join(text_nodes).split()).strip()
    return normalized


def _build_segments(text: str, count: int) -> list[str]:
    normalized = text.strip() or "Uploaded source material."
    if count <= 0:
        return [normalized]

    chunk_size = max(1, len(normalized) // count)
    segments: list[str] = []
    for index in range(count):
        start = index * chunk_size
        end = len(normalized) if index == count - 1 else min(len(normalized), start + chunk_size)
        segment = normalized[start:end].strip() or normalized
        segments.append(segment)
    return segments
