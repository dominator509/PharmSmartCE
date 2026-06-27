from __future__ import annotations

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.services.auth.service import AuthService

router = APIRouter(prefix="/auth")


class RegisterDTO(BaseModel):
    email: str
    password: str


class LoginDTO(BaseModel):
    email: str
    password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterDTO) -> Response:
    await AuthService().register(payload.email, payload.password)
    return Response(status_code=status.HTTP_201_CREATED)


@router.post("/login")
async def login(payload: LoginDTO) -> Response:
    await AuthService().login(payload.email, payload.password)
    return Response(status_code=status.HTTP_200_OK)


@router.post("/refresh")
async def refresh() -> Response:
    await AuthService().refresh()
    return Response(status_code=status.HTTP_200_OK)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> Response:
    await AuthService().logout()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
