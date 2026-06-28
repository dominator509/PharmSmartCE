from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.api.deps import get_settings

router = APIRouter()


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


async def _check_database(database_url: str) -> bool:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    try:
        async with engine.connect() as connection:
            await asyncio.wait_for(connection.execute(text("SELECT 1")), timeout=0.5)
        return True
    except Exception:
        return False
    finally:
        await engine.dispose()


@router.get("/readyz")
async def readyz(request: Request) -> Response:
    settings = get_settings(request)
    db_ready = await _check_database(settings.database_url)
    faiss_ready = Path(settings.faiss_index_dir).exists()
    llm_ready = bool(getattr(request.app.state, "llm_ready", True))
    payload = {"db": db_ready, "faiss": faiss_ready, "llm": llm_ready}
    status_code = (
        status.HTTP_200_OK if all(payload.values()) else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(content=payload, status_code=status_code)


@router.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
