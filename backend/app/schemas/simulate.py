from decimal import Decimal

from pydantic import BaseModel, Field


class SimulateRequest(BaseModel):
    face_value: Decimal = Field(gt=0)
    base_rate: Decimal = Field(ge=0)
    term_months: int = Field(ge=0)
    receivable_type: str
    currency_code: str = Field(min_length=3, max_length=3)
    payment_currency_code: str = Field(min_length=3, max_length=3)


class SimulateResponse(BaseModel):
    face_value: Decimal
    present_value: Decimal
    base_rate: Decimal
    spread_applied: Decimal
    term_months: int
    currency_code: str
    payment_currency_code: str
    exchange_rate_used: Decimal | None
    present_value_in_payment_currency: Decimal
