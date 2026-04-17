from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories import cedente_repository
from app.schemas.cedentes import CedenteCreate, CedenteResponse

router = APIRouter(prefix="/cedentes", tags=["Cedentes"])


@router.get("", response_model=list[CedenteResponse])
async def list_cedentes(session: AsyncSession = Depends(get_session)):
    return await cedente_repository.list_all(session)


@router.post("", response_model=CedenteResponse, status_code=status.HTTP_201_CREATED)
async def create_cedente(
    data: CedenteCreate,
    session: AsyncSession = Depends(get_session),
):
    existing = await cedente_repository.get_by_document(session, data.document)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cedente with document {data.document} already exists",
        )
    cedente = await cedente_repository.create(session, name=data.name, document=data.document)
    await session.commit()
    return cedente
