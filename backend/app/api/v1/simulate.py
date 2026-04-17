import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.simulate import SimulateRequest, SimulateResponse
from app.services.pricing_service import price_receivable

logger = structlog.get_logger()

router = APIRouter(tags=["Simulation"])


@router.post("/simulate", response_model=SimulateResponse)
async def simulate(
    data: SimulateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Calculates present value without persisting. Supports cross-currency."""
    result = await price_receivable(
        session,
        face_value=data.face_value,
        base_rate=data.base_rate,
        term_months=data.term_months,
        receivable_type=data.receivable_type,
        currency_code=data.currency_code,
        payment_currency_code=data.payment_currency_code,
    )

    logger.debug(
        "simulation.computed",
        face_value=str(data.face_value),
        spread=str(result.spread_applied),
        present_value=str(result.present_value),
        cross_currency=(data.currency_code.upper() != data.payment_currency_code.upper()),
    )

    return SimulateResponse(
        face_value=data.face_value,
        present_value=result.present_value,
        base_rate=data.base_rate,
        spread_applied=result.spread_applied,
        term_months=data.term_months,
        currency_code=result.currency_code,
        payment_currency_code=result.payment_currency_code,
        exchange_rate_used=result.exchange_rate_used,
        present_value_in_payment_currency=result.present_value_in_payment_currency,
    )
