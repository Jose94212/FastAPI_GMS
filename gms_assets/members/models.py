"""
DB model for the Members resource - the central entity everything else (Staff,
Subscriptions, Locker) links back to via member_id.
"""
from datetime import date
from typing import Optional, List

from sqlmodel import Field, Relationship

from gms_assets.locker.models import GymLockerDB
from gms_assets.member_subscriptions.model import GymSubscriptionsDB
from gms_assets.members.schemas import GymMembersCreate
from gms_assets.staff.model import GymStaffsDB


class GymMembersDB(GymMembersCreate, table=True):
    """
    DB-table created as per this class. Every relationship here has cascade_delete=True:
    deleting a member also deletes their linked staff row, subscriptions, and locker.
    """
    member_id: Optional[int] = Field(default=None, primary_key=True)
    created_date: date = Field(default_factory=date.today)
    updated_date: date = Field(default_factory=date.today)

    staff: Optional["GymStaffsDB"] = Relationship(back_populates="member", cascade_delete=True)
    subscriptions: List["GymSubscriptionsDB"] = Relationship(back_populates="member", cascade_delete=True)
    locker: Optional["GymLockerDB"] = Relationship(back_populates="member", cascade_delete=True)

