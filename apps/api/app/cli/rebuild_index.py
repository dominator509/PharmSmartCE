from __future__ import annotations

import argparse
import asyncio
import hashlib
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.adapters.storage import FaissStore
from app.config import Settings
from app.repositories.models.chunks import ChunkModel
from app.repositories.models.courses import CourseModel
from app.repositories.models.sources import SourceModel


@dataclass(slots=True)
class ChunkRow:
    id: str
    source_id: str
    page: int
    span_start: int
    span_end: int
    text: str


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rebuild_index")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Rebuild FAISS indices for every course in the database.",
    )
    args = parser.parse_args(argv)
    if not args.all:
        parser.error("the --all flag is required")

    asyncio.run(_run_all())
    print("rebuild index: ok")
    return 0


async def _run_all() -> None:
    settings = Settings()
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            course_ids = await _course_ids(session)
            for course_id in course_ids:
                rows = await _chunk_rows(session, course_id)
                rebuilt = _rebuild_course_index(
                    course_id=course_id,
                    rows=rows,
                    index_dir=Path(settings.faiss_index_dir),
                )
                if rebuilt == 0:
                    print(f"(rebuild index: {course_id} has no chunks; cleared stale artifacts)")
                else:
                    print(f"(rebuild index: {course_id} rebuilt {rebuilt} chunks)")
    finally:
        await engine.dispose()


async def _course_ids(session: AsyncSession) -> list[str]:
    result = await session.execute(select(CourseModel.id).order_by(CourseModel.id))
    return [str(course_id) for course_id in result.scalars()]


async def _chunk_rows(session: AsyncSession, course_id: str) -> list[ChunkRow]:
    query = (
        select(
            ChunkModel.id,
            ChunkModel.source_id,
            ChunkModel.page,
            ChunkModel.span_start,
            ChunkModel.span_end,
            ChunkModel.text,
        )
        .join(SourceModel, SourceModel.id == ChunkModel.source_id)
        .where(SourceModel.course_id == course_id)
        .order_by(ChunkModel.embedding_index, ChunkModel.page, ChunkModel.id)
    )
    result = await session.execute(query)
    return [
        ChunkRow(
            id=str(row.id),
            source_id=str(row.source_id),
            page=int(row.page),
            span_start=int(row.span_start),
            span_end=int(row.span_end),
            text=str(row.text),
        )
        for row in result.all()
    ]


def _rebuild_course_index(course_id: str, rows: list[ChunkRow], index_dir: Path) -> int:
    store = FaissStore(course_id, index_dir)
    store.reset()
    if not rows:
        return 0

    vectors = _embed_texts([row.text for row in rows])
    metadata = [
        {
            "source_id": row.source_id,
            "page": row.page,
            "span_start": row.span_start,
            "span_end": row.span_end,
            "text": row.text,
        }
        for row in rows
    ]
    store.add([row.id for row in rows], vectors, metadata)
    return len(rows)


def _embed_texts(texts: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for text in texts:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector = [
            int.from_bytes(digest[offset : offset + 2], "big") / 65535.0
            for offset in range(0, 16, 2)
        ]
        vectors.append(vector)
    return vectors


if __name__ == "__main__":
    raise SystemExit(main())
