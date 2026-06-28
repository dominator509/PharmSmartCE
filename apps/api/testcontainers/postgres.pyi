from __future__ import annotations

from collections.abc import Iterator


class PostgresContainer:
    def __init__(
        self,
        image: str,
        username: str,
        password: str,
        dbname: str,
        driver: str | None = ...,
    ) -> None: ...
    def __enter__(self) -> PostgresContainer: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> bool | None: ...
    def get_connection_url(self) -> str: ...
