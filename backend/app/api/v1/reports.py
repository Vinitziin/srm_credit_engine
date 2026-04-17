import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories import statement_repository
from app.schemas.statements import StatementFilters, StatementPage

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/statements", response_model=StatementPage)
async def get_statements(
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    cedente_id: uuid.UUID | None = Query(None),
    currency_code: str | None = Query(None, min_length=3, max_length=3),
    status: str | None = Query(None, max_length=20),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> StatementPage:
    """Liquidation statement with server-side pagination and filters.

    `currency_code` filters by payment currency (the settlement currency).
    """
    filters = StatementFilters(
        date_from=date_from,
        date_to=date_to,
        cedente_id=cedente_id,
        payment_currency_code=currency_code,
        status=status,
    )
    total = await statement_repository.count(session, filters)
    items = await statement_repository.list_paginated(
        session, filters, page=page, page_size=page_size
    )
    return StatementPage(page=page, page_size=page_size, total=total, items=items)
