from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from hris_bpe.bootstrap.router import api_router
from hris_bpe.common.responses import error_payload
from hris_bpe.config.settings import get_settings
from hris_bpe.migrations.runner import upgrade_database


def create_application() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
    )

    if settings.auto_migrate_on_startup:

        @app.on_event("startup")
        def _apply_startup_migrations() -> None:
            upgrade_database()

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(
                message=str(exc.detail),
                errors=[{"code": "http_error", "detail": str(exc.detail)}],
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_payload(
                message="Validasi request gagal.",
                errors=[
                    {
                        "code": "validation_error",
                        "detail": item.get("msg"),
                        "field": ".".join(str(part) for part in item.get("loc", [])),
                    }
                    for item in exc.errors()
                ],
            ),
        )

    @app.get("/health")
    def healthcheck() -> dict:
        return {
            "status": "ok",
            "service": settings.app_name,
            "environment": settings.app_env,
        }

    app.include_router(api_router)
    return app

