from abc import ABC, abstractmethod
from decimal import Decimal


class PricingStrategy(ABC):
    """Base class for receivable pricing strategies.

    Subclasses define the spread rate for each receivable type.
    The present value formula is:
        PV = face_value / (1 + base_rate + spread) ^ term_months
    """

    @abstractmethod
    def get_spread(self) -> Decimal: ...

    def calculate_present_value(
        self, face_value: Decimal, base_rate: Decimal, term_months: int
    ) -> Decimal:
        rate = Decimal(1) + base_rate + self.get_spread()
        pv = face_value / rate**term_months
        return pv.quantize(Decimal("0.00000001"))
