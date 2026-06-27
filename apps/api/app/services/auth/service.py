from __future__ import annotations


class AuthService:
    async def register(self, email: str, password: str) -> None:
        raise NotImplementedError("AuthService.register is not implemented yet.")

    async def login(self, email: str, password: str) -> None:
        raise NotImplementedError("AuthService.login is not implemented yet.")

    async def refresh(self) -> None:
        raise NotImplementedError("AuthService.refresh is not implemented yet.")

    async def logout(self) -> None:
        raise NotImplementedError("AuthService.logout is not implemented yet.")
