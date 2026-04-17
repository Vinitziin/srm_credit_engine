from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories import currency_repository, exchange_rate_repository
from app.schemas.exchange_rates import ExchangeRateCreate, ExchangeRateResponse
from app.services import exchange_rate_client

router = APIRouter(prefix="/exchange-rates", tags=["Exchange Rates"])


async def _resolve_currencies(session: AsyncSession, from_code: str, to_code: str):
    """Resolves currency codes to ORM objects, raising 404 if not found."""
    from_curr = await currency_repository.get_by_code(session, from_code)
    if from_curr is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Currency '{from_code}' not found",
        )
    to_curr = await currency_repository.get_by_code(session, to_code)
    if to_curr is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Currency '{to_code}' not found",
        )
    return from_curr, to_curr


def _build_response(exchange_rate, from_code: str, to_code: str) -> ExchangeRateResponse:
    return ExchangeRateResponse(
        id=exchange_rate.id,
        from_currency_code=from_code,
        to_currency_code=to_code,
        rate=exchange_rate.rate,
        effective_date=exchange_rate.effective_date,
    )


@router.get("", response_model=ExchangeRateResponse)
async def get_latest_rate(
    from_currency: str = Query(min_length=3, max_length=3),
    to_currency: str = Query(min_length=3, max_length=3),
    session: AsyncSession = Depends(get_session),
):
    row = await exchange_rate_repository.get_latest(
        session, from_currency.upper(), to_currency.upper()
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange rate not found",
        )
    exchange_rate, from_code, to_code = row
    return _build_response(exchange_rate, from_code, to_code)


@router.post("", response_model=ExchangeRateResponse, status_code=status.HTTP_201_CREATED)
async def create_exchange_rate(
    data: ExchangeRateCreate,
    session: AsyncSession = Depends(get_session),
):
    from_curr, to_curr = await _resolve_currencies(
        session, data.from_currency_code.upper(), data.to_currency_code.upper()
    )
    exchange_rate = await exchange_rate_repository.create(
        session, from_curr.id, to_curr.id, data.rate
    )
    await session.commit()
    return _build_response(exchange_rate, from_curr.code, to_curr.code)


@router.post(
    "/fetch",
    response_model=ExchangeRateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def fetch_external_rate(
    from_currency: str = Query(min_length=3, max_length=3),
    to_currency: str = Query(min_length=3, max_length=3),
    session: AsyncSession = Depends(get_session),
):
    """Fetches rate from mocked external API (with retry) and persists it."""
    from_code = from_currency.upper()
    to_code = to_currency.upper()

    from_curr, to_curr = await _resolve_currencies(session, from_code, to_code)
    rate = await exchange_rate_client.fetch_external_rate(from_code, to_code)
    exchange_rate = await exchange_rate_repository.create(session, from_curr.id, to_curr.id, rate)
    await session.commit()
    return _build_response(exchange_rate, from_code, to_code)
