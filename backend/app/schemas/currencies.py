import uuid

from pydantic import BaseModel


class CurrencyResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str

    model_config = {"from_attributes": True}
