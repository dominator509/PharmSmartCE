from __future__ import annotations

import hashlib
import json
import re

from app.services.generation.grounded_llm import INSUFFICIENT_CONTEXT_MARKER


class FakeLLM:
    def generate(self, prompt: str, max_tokens: int) -> str:
        del max_tokens
        if "<<<context_start" not in prompt or "<<<context_end>>>" not in prompt:
            return INSUFFICIENT_CONTEXT_MARKER

        context_match = re.search(
            r"<<<context_start(?: [^>]*)?>>>\s*(.*?)\s*<<<context_end>>>",
            prompt,
            flags=re.DOTALL,
        )
        if context_match is None:
            return INSUFFICIENT_CONTEXT_MARKER

        context_text = " ".join(context_match.group(1).split())
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        answer_index = int(digest[:2], 16) % 4
        key_phrase = " ".join(context_text.split()[:6]) or "the supplied context"

        choices = [
            f"Supported by the source: {key_phrase}",
            f"Not supported option {digest[2:6]}",
            f"Not supported option {digest[6:10]}",
            f"Not supported option {digest[10:14]}",
        ]
        choices[answer_index] = f"Supported by the source: {key_phrase}"

        payload = {
            "stem": f"What is the best answer based on: {key_phrase}?",
            "choices": choices,
            "correct_choice_index": answer_index,
            "rationale": f"The source text says: {context_text}",
            "prompt_hash": digest[:16],
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)
