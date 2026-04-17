from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.receivable_types import ReceivableType


async def list_all(session: AsyncSession) -> list[ReceivableType]:
    result = await session.execute(
        select(ReceivableType).order_by(ReceivableType.name)
    )
    return list(result.scalars().all())
