from __future__ import annotations

import os
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
    if filename.rstrip(" .") != filename:
        raise ValueError("Source filename must not end with dots or spaces.")
    if os.name == "nt" and _is_windows_reserved_filename(filename):
        raise ValueError("Source filename must not use reserved Windows names.")


def _is_windows_reserved_filename(filename: str) -> bool:
    stem = filename.split(".", 1)[0].upper()
    return stem in {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
