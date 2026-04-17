"""seed currencies, receivable types and initial exchange rate

Revision ID: b2f1c3d4e5a6
Revises: a74fd0848ea6
Create Date: 2026-04-17 05:10:00.000000

"""
import uuid
from datetime import date
from decimal import Decimal
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2f1c3d4e5a6"
down_revision: Union[str, None] = "a74fd0848ea6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Fixed UUIDs for seed data (deterministic for the downgrade)
BRL_ID = uuid.uuid4()
USD_ID = uuid.uuid4()


def upgrade() -> None:
    currencies = sa.table(
        "currencies",
        sa.column("id", sa.Uuid),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
    )
    op.bulk_insert(
        currencies,
        [
            {"id": BRL_ID, "code": "BRL", "name": "Real Brasileiro"},
            {"id": USD_ID, "code": "USD", "name": "US Dollar"},
        ],
    )

    receivable_types = sa.table(
        "receivable_types",
        sa.column("id", sa.Uuid),
        sa.column("name", sa.String),
        sa.column("spread_rate", sa.Numeric),
    )
    op.bulk_insert(
        receivable_types,
        [
            {
                "id": uuid.uuid4(),
                "name": "Duplicata Mercantil",
                "spread_rate": Decimal("0.015000"),
            },
            {
                "id": uuid.uuid4(),
                "name": "Cheque Pré-datado",
                "spread_rate": Decimal("0.025000"),
            },
        ],
    )

    exchange_rates = sa.table(
        "exchange_rates",
        sa.column("id", sa.Uuid),
        sa.column("from_currency_id", sa.Uuid),
        sa.column("to_currency_id", sa.Uuid),
        sa.column("rate", sa.Numeric),
        sa.column("effective_date", sa.Date),
    )
    op.bulk_insert(
        exchange_rates,
        [
            {
                "id": uuid.uuid4(),
                "from_currency_id": USD_ID,
                "to_currency_id": BRL_ID,
                "rate": Decimal("5.25000000"),
                "effective_date": date.today(),
            },
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM exchange_rates")
    op.execute("DELETE FROM receivable_types")
    op.execute("DELETE FROM currencies")
