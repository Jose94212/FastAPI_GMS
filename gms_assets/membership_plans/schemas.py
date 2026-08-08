"""
Schemas for the Membership Plans resource - the gym's catalog of subscribable plans
(what a member_subscriptions row actually points at via plan_id).
"""
from __future__ import annotations

from enum import Enum

from sqlmodel import SQLModel, Field


class PlanNames(str, Enum):
    """
    Names of the membership plans the gym offers.
    """
    cardio = "Cardio"
    weight = "Weight"
    weight_cardio = "Weight and Cardio training"
    yoga = "Yoga"


class GymMembershipPlansCreate(SQLModel):
    """
    Details required for adding a new membership plan. No id here - the DB assigns it.
    """
    plan_name: PlanNames = Field(default=PlanNames.weight, description="Cardio/Weight/weight_cardio")
    price: int | None = Field(ge=1000, default=1000)
    duration_months: int | None = Field(default=1, description="Number of months")
