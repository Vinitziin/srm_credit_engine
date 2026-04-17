from fastapi import APIRouter

from app.api.v1.cedentes import router as cedentes_router
from app.api.v1.currencies import router as currencies_router
from app.api.v1.exchange_rates import router as exchange_rates_router
from app.api.v1.receivable_types import router as receivable_types_router
from app.api.v1.reports import router as reports_router
from app.api.v1.simulate import router as simulate_router
from app.api.v1.transactions import router as transactions_router

router = APIRouter(prefix="/api/v1")
router.include_router(currencies_router)
router.include_router(exchange_rates_router)
router.include_router(receivable_types_router)
router.include_router(cedentes_router)
router.include_router(simulate_router)
router.include_router(transactions_router)
router.include_router(reports_router)

