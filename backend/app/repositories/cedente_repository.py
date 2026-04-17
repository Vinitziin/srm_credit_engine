import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cedentes import Cedente


async def list_all(session: AsyncSession) -> list[Cedente]:
    result = await session.execute(select(Cedente).order_by(Cedente.name))
    return list(result.scalars().all())


async def get_by_id(session: AsyncSession, cedente_id: uuid.UUID) -> Cedente | None:
    result = await session.execute(select(Cedente).where(Cedente.id == cedente_id))
    return result.scalar_one_or_none()


async def get_by_document(session: AsyncSession, document: str) -> Cedente | None:
    result = await session.execute(select(Cedente).where(Cedente.document == document))
    return result.scalar_one_or_none()


async def create(session: AsyncSession, *, name: str, document: str) -> Cedente:
    cedente = Cedente(name=name, document=document)
    session.add(cedente)
    await session.flush()
    return cedente
