import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.currencies import Currency
from app.models.exchange_rates import ExchangeRate


async def get_latest(
    session: AsyncSession, from_code: str, to_code: str
) -> tuple[ExchangeRate, str, str] | None:
    """Returns the latest exchange rate for a currency pair, with currency codes."""
    from_curr = aliased(Currency)
    to_curr = aliased(Currency)

    stmt = (
        select(ExchangeRate, from_curr.code, to_curr.code)
        .join(from_curr, ExchangeRate.from_currency_id == from_curr.id)
        .join(to_curr, ExchangeRate.to_currency_id == to_curr.id)
        .where(from_curr.code == from_code)
        .where(to_curr.code == to_code)
        .order_by(ExchangeRate.effective_date.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.first()


async def create(
    session: AsyncSession,
    from_currency_id: uuid.UUID,
    to_currency_id: uuid.UUID,
    rate: Decimal,
) -> ExchangeRate:
    exchange_rate = ExchangeRate(
        from_currency_id=from_currency_id,
        to_currency_id=to_currency_id,
        rate=rate,
        effective_date=date.today(),
    )
    session.add(exchange_rate)
    await session.flush()
    return exchange_rate
