from dataclasses import dataclass
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import exchange_rate_repository
from app.services.pricing import get_strategy


@dataclass(frozen=True)
class PricingResult:
    present_value: Decimal
    spread_applied: Decimal
    exchange_rate_used: Decimal | None
    present_value_in_payment_currency: Decimal
    currency_code: str
    payment_currency_code: str


async def price_receivable(
    session: AsyncSession,
    *,
    face_value: Decimal,
    base_rate: Decimal,
    term_months: int,
    receivable_type: str,
    currency_code: str,
    payment_currency_code: str,
) -> PricingResult:
    """Resolves strategy, computes PV and applies cross-currency conversion.

    Raises HTTPException(400) for unknown receivable types and
    HTTPException(404) when a required FX rate is missing.
    """
    try:
        strategy = get_strategy(receivable_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    pv = strategy.calculate_present_value(face_value, base_rate, term_months)

    from_code = currency_code.upper()
    to_code = payment_currency_code.upper()
    exchange_rate_used: Decimal | None = None
    pv_in_payment = pv

    if from_code != to_code:
        row = await exchange_rate_repository.get_latest(session, from_code, to_code)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No exchange rate found for {from_code}/{to_code}",
            )
        exchange_rate, _, _ = row
        exchange_rate_used = exchange_rate.rate
        pv_in_payment = (pv * exchange_rate_used).quantize(pv)

    return PricingResult(
        present_value=pv,
        spread_applied=strategy.get_spread(),
        exchange_rate_used=exchange_rate_used,
        present_value_in_payment_currency=pv_in_payment,
        currency_code=from_code,
        payment_currency_code=to_code,
    )
