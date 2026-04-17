from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories import receivable_type_repository
from app.schemas.receivable_types import ReceivableTypeResponse

router = APIRouter(prefix="/receivable-types", tags=["Receivable Types"])


@router.get("", response_model=list[ReceivableTypeResponse])
async def list_receivable_types(
    session: AsyncSession = Depends(get_session),
):
    return await receivable_type_repository.list_all(session)
