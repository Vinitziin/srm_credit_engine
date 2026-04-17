from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories import currency_repository
from app.schemas.currencies import CurrencyResponse

router = APIRouter(prefix="/currencies", tags=["Currencies"])


@router.get("", response_model=list[CurrencyResponse])
async def list_currencies(
    session: AsyncSession = Depends(get_session),
):
    return await currency_repository.list_all(session)
