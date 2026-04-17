import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    cedente_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cedentes.id"), nullable=False, index=True
    )
    receivable_type_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("receivable_types.id"), nullable=False
    )
    face_value: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    present_value: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    currency_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("currencies.id"), nullable=False, index=True
    )
    payment_currency_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("currencies.id"), nullable=False, index=True
    )
    exchange_rate_used: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8), nullable=True
    )
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    base_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    spread_applied: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="SETTLED"
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), index=True
    )

    __mapper_args__ = {"version_id_col": version}
