from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from app.config import get_settings
from app.exceptions import http_exception_handler, unhandled_exception_handler
from app.logging import RequestIdMiddleware, setup_logging

settings = get_settings()
setup_logging(settings.LOG_LEVEL)

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

app.add_middleware(RequestIdMiddleware)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

from app.api.v1 import router as v1_router  # noqa: E402

app.include_router(v1_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
