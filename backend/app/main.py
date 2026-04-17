from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from app.config import get_settings
from app.exceptions import (
    http_exception_handler,
    integrity_error_handler,
    stale_data_handler,
    unhandled_exception_handler,
)
from app.logging import RequestIdMiddleware, setup_logging

settings = get_settings()
setup_logging(settings.LOG_LEVEL)

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StaleDataError, stale_data_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

from app.api.v1 import router as v1_router  # noqa: E402

app.include_router(v1_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
