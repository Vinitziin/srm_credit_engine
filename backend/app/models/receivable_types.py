from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ReceivableType(Base):
    __tablename__ = "receivable_types"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    spread_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
