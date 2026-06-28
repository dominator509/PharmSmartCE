from __future__ import annotations

from typing import Protocol


class StoragePort(Protocol):
    async def save_source(
        self,
        course_id: str,
        source_id: str,
        filename: str,
        content: bytes,
    ) -> str: ...

    async def load_source(
        self,
        course_id: str,
        source_id: str,
        filename: str,
    ) -> bytes: ...
