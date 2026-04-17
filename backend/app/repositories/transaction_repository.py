import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transactions import Transaction


async def create(
    session: AsyncSession,
    *,
    cedente_id: uuid.UUID,
    receivable_type_id: uuid.UUID,
    face_value: Decimal,
    present_value: Decimal,
    currency_id: uuid.UUID,
    payment_currency_id: uuid.UUID,
    exchange_rate_used: Decimal | None,
    term_months: int,
    base_rate: Decimal,
    spread_applied: Decimal,
    status: str = "SETTLED",
) -> Transaction:
    transaction = Transaction(
        cedente_id=cedente_id,
        receivable_type_id=receivable_type_id,
        face_value=face_value,
        present_value=present_value,
        currency_id=currency_id,
        payment_currency_id=payment_currency_id,
        exchange_rate_used=exchange_rate_used,
        term_months=term_months,
        base_rate=base_rate,
        spread_applied=spread_applied,
        status=status,
    )
    session.add(transaction)
    await session.flush()
    return transaction


async def get_by_id(session: AsyncSession, transaction_id: uuid.UUID) -> Transaction | None:
    result = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
    return result.scalar_one_or_none()
