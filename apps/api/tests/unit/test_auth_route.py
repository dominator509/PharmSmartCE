from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.api.routes.auth import ChangePasswordDTO, LoginDTO, RegisterDTO


@pytest.mark.parametrize(
    "dto_type, kwargs",
    [
        (RegisterDTO, {"email": "pharmacist@example.com", "password": 123456789012}),
        (LoginDTO, {"email": "pharmacist@example.com", "password": True}),
        (
            ChangePasswordDTO,
            {"current_password": False, "new_password": "newsecretsecret12"},
        ),
    ],
)
def test_auth_dtos_reject_non_string_password_fields(dto_type, kwargs) -> None:
    with pytest.raises(ValidationError):
        dto_type(**kwargs)
