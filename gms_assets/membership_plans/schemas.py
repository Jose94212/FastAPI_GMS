from __future__ import annotations

from enum import Enum

from sqlmodel import SQLModel, Field


class PlanNames(str, Enum):
    """

    """
    cardio = "Cardio"
    weight = "Weight"
    weight_cardio = "Weight and Cardio training"
    yoga = "Yoga"


class GymMembershipPlansCreate(SQLModel):
    """

    """
    plan_name: PlanNames = Field(default=PlanNames.weight, description="Cardio/Weight/weight_cardio")
    price: int | None = Field(ge=1000, default=1000)
    duration_months: int | None = Field(default=1, description="Number of months")
