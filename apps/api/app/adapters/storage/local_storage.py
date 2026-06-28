from __future__ import annotations

from pathlib import Path


class LocalSourceStorage:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    async def save_source(
        self,
        course_id: str,
        source_id: str,
        filename: str,
        content: bytes,
    ) -> str:
        target = self.root / course_id / source_id / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return str(target.relative_to(self.root))

    async def load_source(
        self,
        course_id: str,
        source_id: str,
        filename: str,
    ) -> bytes:
        target = self.root / course_id / source_id / filename
        return target.read_bytes()
