from __future__ import annotations

import asyncio

import pytest

from app.adapters.storage.local_storage import LocalSourceStorage


def test_local_source_storage_rejects_path_like_filename(tmp_path) -> None:
    storage = LocalSourceStorage(tmp_path / "uploads")

    async def _run() -> None:
        await storage.save_source("course-1", "source-1", "../evil.pdf", b"data")

    with pytest.raises(ValueError):
        asyncio.run(_run())
