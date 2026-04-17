from app.services.pricing.base import PricingStrategy
from app.services.pricing.cheque import ChequeStrategy
from app.services.pricing.duplicata import DuplicataStrategy

_STRATEGIES: dict[str, PricingStrategy] = {
    "Duplicata Mercantil": DuplicataStrategy(),
    "Cheque Pré-datado": ChequeStrategy(),
}


def get_strategy(receivable_type_name: str) -> PricingStrategy:
    """Returns the pricing strategy for a given receivable type name.

    Raises ValueError if the type is not recognized.
    """
    strategy = _STRATEGIES.get(receivable_type_name)
    if strategy is None:
        raise ValueError(f"Unknown receivable type: '{receivable_type_name}'")
    return strategy
