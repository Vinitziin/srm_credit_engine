import uuid
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


@dataclass(frozen=True)
class StatementFilters:
    date_from: date | None = None
    date_to: date | None = None
    cedente_id: uuid.UUID | None = None
    payment_currency_code: str | None = None
    status: str | None = None


class StatementItem(BaseModel):
    id: uuid.UUID
    created_at: datetime
    cedente_name: str
    cedente_document: str
    receivable_type: str
    face_value: Decimal
    present_value: Decimal
    currency_code: str
    payment_currency_code: str
    exchange_rate_used: Decimal | None
    status: str


class StatementPage(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[StatementItem]
