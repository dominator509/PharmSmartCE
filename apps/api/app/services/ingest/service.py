from __future__ import annotations


class IngestService:
    async def enqueue(self, source_id: str) -> None:
        raise NotImplementedError("IngestService.enqueue is not implemented yet.")
