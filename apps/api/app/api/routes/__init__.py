from app.api.routes.auth import router as auth_router
from app.api.routes.courses import router as courses_router
from app.api.routes.health import router as health_router
from app.api.routes.sessions import ce_records_router
from app.api.routes.sessions import router as sessions_router

__all__ = ["auth_router", "courses_router", "health_router", "sessions_router", "ce_records_router"]
