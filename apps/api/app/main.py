from fastapi import FastAPI

from app.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    _settings = settings or Settings()
    app = FastAPI(title="PharmSmartCE API")

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
