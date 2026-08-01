"""
Schemas manage how data enters and exits your API via HTTP.
They validate incoming JSON requests, filter outgoing JSON responses,
and automatically generate your interactive Swagger/OpenAPI Documentation.

NOTE: inherited from SQLModel (not plain Pydantic BaseModel) so that
'models.py' can inherit these same fields instead of duplicating them.
"""
from __future__ import annotations

from datetime import date

from sqlmodel import SQLModel, Field


class FurnitureDetailsCreate(SQLModel):
    """
    Details required for adding new furniture. No id here - the DB assigns it.
    """
    fur_name: str = Field(max_length=100)
    fur_description: str | None = Field(default=None, max_length=200)
    fur_count: int = Field(ge=0)
    fur_purchase_date: date | None = Field(default_factory=date.today)
    fur_cost: int = Field(gt=0)
