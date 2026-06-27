from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request

from app.api import install_exception_handlers
from app.api.handlers import bind_request_id, reset_request_id
from app.api.routes import auth_router, health_router
from app.config import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    Path(settings.faiss_index_dir).mkdir(parents=True, exist_ok=True)
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(title="PharmSmartCE API", lifespan=lifespan)
    app.state.settings = settings or Settings()
    app.state.llm_ready = True

    install_exception_handlers(app)

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        token = None
        request_id = uuid4().hex
        try:
            token = bind_request_id(request_id)
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            if token is not None:
                reset_request_id(token)

    app.include_router(health_router)
    app.include_router(auth_router)
    return app


app = create_app()
