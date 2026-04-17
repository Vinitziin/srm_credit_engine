import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    cedente_id: uuid.UUID
    receivable_type: str
    face_value: Decimal = Field(gt=0)
    base_rate: Decimal = Field(ge=0)
    term_months: int = Field(ge=0)
    currency_code: str = Field(min_length=3, max_length=3)
    payment_currency_code: str = Field(min_length=3, max_length=3)


class TransactionResponse(BaseModel):
    id: uuid.UUID
    cedente_id: uuid.UUID
    receivable_type_id: uuid.UUID
    face_value: Decimal
    present_value: Decimal
    currency_id: uuid.UUID
    payment_currency_id: uuid.UUID
    exchange_rate_used: Decimal | None
    term_months: int
    base_rate: Decimal
    spread_applied: Decimal
    status: str
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=20)
    version: int = Field(ge=1)
