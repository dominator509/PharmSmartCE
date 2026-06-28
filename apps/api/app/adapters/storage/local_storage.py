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
        _ensure_plain_filename(filename)
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
        _ensure_plain_filename(filename)
        target = self.root / course_id / source_id / filename
        return target.read_bytes()


def _ensure_plain_filename(filename: str) -> None:
    if not filename.strip():
        raise ValueError("Source filename must not be empty.")
    if filename != Path(filename).name or filename in {".", ".."}:
        raise ValueError("Source filename must not include path separators.")
