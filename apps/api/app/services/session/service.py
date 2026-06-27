from __future__ import annotations


class SessionService:
    async def record_answer(self, session_id: str, question_id: str, chosen_index: int) -> None:
        raise NotImplementedError("SessionService.record_answer is not implemented yet.")
