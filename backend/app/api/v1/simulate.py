from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories import exchange_rate_repository
from app.schemas.simulate import SimulateRequest, SimulateResponse
from app.services.pricing import get_strategy

router = APIRouter(tags=["Simulation"])


@router.post("/simulate", response_model=SimulateResponse)
async def simulate(
    data: SimulateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Calculates present value without persisting. Supports cross-currency."""
    try:
        strategy = get_strategy(data.receivable_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    pv = strategy.calculate_present_value(
        data.face_value, data.base_rate, data.term_months
    )

    exchange_rate_used = None
    pv_in_payment = pv

    if data.currency_code.upper() != data.payment_currency_code.upper():
        row = await exchange_rate_repository.get_latest(
            session, data.currency_code.upper(), data.payment_currency_code.upper()
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"No exchange rate found for "
                    f"{data.currency_code.upper()}/{data.payment_currency_code.upper()}"
                ),
            )
        exchange_rate, _, _ = row
        exchange_rate_used = exchange_rate.rate
        pv_in_payment = (pv * exchange_rate_used).quantize(pv)

    return SimulateResponse(
        face_value=data.face_value,
        present_value=pv,
        base_rate=data.base_rate,
        spread_applied=strategy.get_spread(),
        term_months=data.term_months,
        currency_code=data.currency_code.upper(),
        payment_currency_code=data.payment_currency_code.upper(),
        exchange_rate_used=exchange_rate_used,
        present_value_in_payment_currency=pv_in_payment,
    )
