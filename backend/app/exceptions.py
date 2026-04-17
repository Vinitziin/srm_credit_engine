import structlog
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

logger = structlog.get_logger()

_PG_UNIQUE_VIOLATION = "23505"


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def stale_data_handler(_request: Request, exc: StaleDataError) -> JSONResponse:
    logger.warning("stale_data", error=str(exc))
    return JSONResponse(
        status_code=409,
        content={"detail": "Record was modified by another process"},
    )


async def integrity_error_handler(
    _request: Request, exc: IntegrityError
) -> JSONResponse:
    # Only unique-constraint violations map cleanly to 409; everything else is a 500.
    pgcode = getattr(getattr(exc, "orig", None), "pgcode", None)
    if pgcode == _PG_UNIQUE_VIOLATION:
        return JSONResponse(
            status_code=409,
            content={"detail": "Unique constraint violation"},
        )
    logger.error("integrity_error", error=str(exc), pgcode=pgcode)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_exception", error=str(exc), exc_type=type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
