"""
Schemas manage how data enters and exits your API via HTTP.
They validate incoming JSON requests, filter outgoing JSON responses,
and automatically generate your interactive Swagger/OpenAPI Documentation.
They inherit from Pydantic's BaseModel

NOTE: here we are inherited from SQLModel.
Later the classes from this will be inherited to 'models' module.
This is being done so that DB and schema are in parity else there are chances of unwanted errors.
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field


class GymElectronicsCreate(SQLModel):
    """
    These are the details required for adding new electronics.
    """
    electro_name: str = Field(max_length=100)
    electro_description: str | None = Field(default=None, max_length=200)
    electro_count: int = Field(ge=0)
