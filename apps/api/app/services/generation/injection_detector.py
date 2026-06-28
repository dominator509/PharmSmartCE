from __future__ import annotations

import re


class InjectionDetector:
    def __init__(self) -> None:
        self._patterns = [
            re.compile(r"ignore (the )?(previous|above|prior) instructions?", re.I),
            re.compile(r"<<<\s*context_(start|end)\s*>>>", re.I),
            re.compile(r"^\s*(system|assistant)\s*:", re.I | re.M),
            re.compile(r"you are (now )?(a|an) .{0,80} (assistant|ai|model)", re.I),
        ]

    def is_flagged(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in self._patterns)
