from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    from_currency_id: Mapped[Decimal] = mapped_column(
        Uuid, ForeignKey("currencies.id"), nullable=False, index=True
    )
    to_currency_id: Mapped[Decimal] = mapped_column(
        Uuid, ForeignKey("currencies.id"), nullable=False, index=True
    )
    rate: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
