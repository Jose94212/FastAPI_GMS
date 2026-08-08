"""
Schemas manage how data enters and exits your API via HTTP.
They validate incoming JSON requests, filter outgoing JSON responses,
and automatically generate your interactive Swagger/OpenAPI Documentation.

NOTE: inherited from SQLModel (not plain Pydantic BaseModel) so that
'models.py' can inherit these same fields instead of duplicating them.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import Enum

from pydantic import model_validator
from sqlmodel import SQLModel, Field


class _GymEquipCategory(str, Enum):
    """
    Broad category an equipment item belongs to.
    """
    free_weights = "free weight"
    cardio = "cardio"
    strength = "strength"


class _GymEquipStatus(str, Enum):
    """
    Operational status of an equipment item.
    """
    operational = "operational"
    under_repair = "under repair"
    retired = "retired"


class GymEquipmentCreate(SQLModel):
    """
    Details required for adding new gym equipment. No id here - the DB assigns it.
    """
    equip_name: str = Field(max_length=100)
    equip_description: str | None = Field(default=None, max_length=1000)
    equip_count: int = Field(gt=0)
    equip_lease: bool = Field(default=False)
    equip_category: _GymEquipCategory = Field(default=_GymEquipCategory.free_weights)
    equip_purchase_date: datetime = Field(default_factory=datetime.utcnow)
    equip_status: _GymEquipStatus = Field(default=_GymEquipStatus.operational)
    equip_cost: int = Field(ge=0)
    equip_cost_total: int | None = Field(default=None, description="If not given, count*cost")
    equip_next_maintenance_date: datetime | None = Field(default=None)

    @model_validator(mode="after")
    def compute_values(self):
        """
        Fills in derived fields left blank by the caller: defaults the next-maintenance
        date to one year after purchase, and the total cost to count * unit cost.
        """
        if not self.equip_next_maintenance_date:
            self.equip_next_maintenance_date = self.equip_purchase_date + timedelta(days=365)
        if not self.equip_cost_total:
            self.equip_cost_total = self.equip_cost * self.equip_count
        return self
