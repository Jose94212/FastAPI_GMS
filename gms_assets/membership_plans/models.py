"""
DB model for the Membership Plans resource.
"""
from __future__ import annotations

from datetime import date, datetime

from sqlmodel import Field

from gms_assets.membership_plans.schemas import GymMembershipPlansCreate


class GymMembershipPlansDB(GymMembershipPlansCreate, table=True):
    """
    DB-table created as per this class.
    """
    plan_id: int | None = Field(primary_key=True, default=None)
    created_date: datetime = Field(default_factory=date.today)
    updated_date: datetime = Field(default_factory=date.today)
