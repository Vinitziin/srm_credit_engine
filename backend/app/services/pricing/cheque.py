from decimal import Decimal

from app.services.pricing.base import PricingStrategy


class ChequeStrategy(PricingStrategy):
    """Pricing strategy for 'Cheque Pré-datado' receivables.

    Spread: 2.5% per month.
    NOTE: This value must stay in sync with the spread_rate column
    in the receivable_types table (seeded as 0.025000).
    """

    def get_spread(self) -> Decimal:
        return Decimal("0.025")
