import uuid
from decimal import Decimal

from pydantic import BaseModel


class ReceivableTypeResponse(BaseModel):
    id: uuid.UUID
    name: str
    spread_rate: Decimal

    model_config = {"from_attributes": True}
