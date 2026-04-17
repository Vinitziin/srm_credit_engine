import uuid

from pydantic import BaseModel, Field


class CedenteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    document: str = Field(min_length=11, max_length=18)


class CedenteResponse(BaseModel):
    id: uuid.UUID
    name: str
    document: str

    model_config = {"from_attributes": True}
