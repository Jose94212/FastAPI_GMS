"""
Schemas manage how data enters and exits your API via HTTP.
They validate incoming JSON requests, filter outgoing JSON responses,
and automatically generate your interactive Swagger/OpenAPI Documentation.

NOTE: inherited from SQLModel (not plain Pydantic BaseModel) so that
'models.py' can inherit these same fields instead of duplicating them.
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field


class GymEquipmentCreate(SQLModel):
    """
    Details required for adding new gym equipment. No id here - the DB assigns it.
    """
    equip_name: str = Field(max_length=100)
    equip_description: str | None = Field(default=None, max_length=1000)
    equip_count: int = Field(gt=0)
    equip_lease: bool = Field(default=False)
