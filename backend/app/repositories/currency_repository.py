from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currencies import Currency


async def list_all(session: AsyncSession) -> list[Currency]:
    result = await session.execute(select(Currency).order_by(Currency.code))
    return list(result.scalars().all())


async def get_by_code(session: AsyncSession, code: str) -> Currency | None:
    result = await session.execute(
        select(Currency).where(Currency.code == code)
    )
    return result.scalar_one_or_none()
