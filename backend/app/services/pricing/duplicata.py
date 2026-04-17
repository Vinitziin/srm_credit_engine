from decimal import Decimal

from app.services.pricing.base import PricingStrategy


class DuplicataStrategy(PricingStrategy):
    """Pricing strategy for 'Duplicata Mercantil' receivables.

    Spread: 1.5% per month.
    NOTE: This value must stay in sync with the spread_rate column
    in the receivable_types table (seeded as 0.015000).
    """

    def get_spread(self) -> Decimal:
        return Decimal("0.015")
