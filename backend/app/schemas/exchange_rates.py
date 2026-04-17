import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ExchangeRateCreate(BaseModel):
    from_currency_code: str = Field(min_length=3, max_length=3)
    to_currency_code: str = Field(min_length=3, max_length=3)
    rate: Decimal = Field(gt=0)


class ExchangeRateResponse(BaseModel):
    id: uuid.UUID
    from_currency_code: str
    to_currency_code: str
    rate: Decimal
    effective_date: date
