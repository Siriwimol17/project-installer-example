"""FastAPI app construction and lifecycle setup."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import Settings
from app.routes import router


def create_app(settings: Settings) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.server = None
        yield

    app = FastAPI(title=settings.service_name, lifespan=lifespan)
    app.state.settings = settings
    app.state.server = None

    @app.middleware("http")
    async def check_loopback_host(request, call_next):
        try:
            from app.security import validate_host

            validate_host(request)
        except Exception as exc:
            from fastapi import HTTPException

            if isinstance(exc, HTTPException):
                return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
            raise
        return await call_next(request)

    app.include_router(router)
    return app
