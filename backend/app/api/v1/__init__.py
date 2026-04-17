from fastapi import APIRouter

from app.api.v1.currencies import router as currencies_router
from app.api.v1.exchange_rates import router as exchange_rates_router
from app.api.v1.receivable_types import router as receivable_types_router

router = APIRouter(prefix="/api/v1")
router.include_router(currencies_router)
router.include_router(exchange_rates_router)
router.include_router(receivable_types_router)
