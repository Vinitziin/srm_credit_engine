import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from app.database import get_session
from app.repositories import (
    cedente_repository,
    currency_repository,
    receivable_type_repository,
    transaction_repository,
)
from app.schemas.transactions import (
    TransactionCreate,
    TransactionResponse,
    TransactionStatusUpdate,
)
from app.services.pricing_service import price_receivable

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    session: AsyncSession = Depends(get_session),
):
    """Liquidates a receivable. Atomic: pricing + persistence in one transaction."""
    cedente = await cedente_repository.get_by_id(session, data.cedente_id)
    if cedente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cedente {data.cedente_id} not found",
        )

    receivable_type = await receivable_type_repository.get_by_name(
        session, data.receivable_type
    )
    if receivable_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Receivable type '{data.receivable_type}' not found",
        )

    currency = await currency_repository.get_by_code(
        session, data.currency_code.upper()
    )
    payment_currency = await currency_repository.get_by_code(
        session, data.payment_currency_code.upper()
    )
    if currency is None or payment_currency is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currency code not found",
        )

    pricing = await price_receivable(
        session,
        face_value=data.face_value,
        base_rate=data.base_rate,
        term_months=data.term_months,
        receivable_type=data.receivable_type,
        currency_code=data.currency_code,
        payment_currency_code=data.payment_currency_code,
    )

    transaction = await transaction_repository.create(
        session,
        cedente_id=cedente.id,
        receivable_type_id=receivable_type.id,
        face_value=data.face_value,
        present_value=pricing.present_value_in_payment_currency,
        currency_id=currency.id,
        payment_currency_id=payment_currency.id,
        exchange_rate_used=pricing.exchange_rate_used,
        term_months=data.term_months,
        base_rate=data.base_rate,
        spread_applied=pricing.spread_applied,
    )
    await session.commit()
    return transaction


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    transaction = await transaction_repository.get_by_id(session, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found",
        )
    return transaction


@router.patch("/{transaction_id}/status", response_model=TransactionResponse)
async def update_transaction_status(
    transaction_id: uuid.UUID,
    data: TransactionStatusUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Updates status with optimistic locking. Returns 409 on version mismatch."""
    transaction = await transaction_repository.get_by_id(session, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found",
        )

    if transaction.version != data.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Version mismatch: expected {transaction.version}, got {data.version}"
            ),
        )

    transaction.status = data.status
    try:
        await session.commit()
    except StaleDataError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction was modified by another process",
        ) from exc
    await session.refresh(transaction)
    return transaction
