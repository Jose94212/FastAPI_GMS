"""
Schemas for the Member Subscriptions resource - links a Member to a Membership Plan
for a given date range.
"""
from __future__ import annotations

from datetime import datetime, date
from enum import Enum

from sqlmodel import SQLModel, Field


class SubscriptionStatus(str, Enum):
    """
    Status of a member's subscription to a plan.
    """
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class GymSubscriptionsCreate(SQLModel):
    """
    Details required for adding a new subscription. No id here - the DB assigns it.
    """
    member_id: int = Field(foreign_key="gymmembersdb.member_id")
    plan_id: int = Field(foreign_key="gymmembershipplansdb.plan_id")
    start_date: date
    end_date: date
    status: SubscriptionStatus = Field(default=SubscriptionStatus.active)
