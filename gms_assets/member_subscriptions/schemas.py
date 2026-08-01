from __future__ import annotations

from datetime import datetime, date
from enum import Enum

from sqlmodel import SQLModel, Field


class SubscriptionStatus(str, Enum):
    """

    """
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class GymSubscriptionsCreate(SQLModel):
    """

    """
    member_id: int = Field(foreign_key="gymmembersdb.member_id")
    plan_id: int = Field(foreign_key="gymmembershipplansdb.plan_id")
    start_date: date
    end_date: date
    status: SubscriptionStatus = Field(default=SubscriptionStatus.active)
