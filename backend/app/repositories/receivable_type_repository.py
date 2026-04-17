from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.receivable_types import ReceivableType


async def list_all(session: AsyncSession) -> list[ReceivableType]:
    result = await session.execute(select(ReceivableType).order_by(ReceivableType.name))
    return list(result.scalars().all())


async def get_by_name(session: AsyncSession, name: str) -> ReceivableType | None:
    result = await session.execute(select(ReceivableType).where(ReceivableType.name == name))
    return result.scalar_one_or_none()
