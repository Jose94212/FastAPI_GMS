from datetime import date
from typing import Optional, List

from sqlmodel import Field, Relationship

from gms_assets.member_subscriptions.model import GymSubscriptionsDB
from gms_assets.members.schemas import GymMembersCreate
from gms_assets.staff.model import GymStaffsDB


class GymMembersDB(GymMembersCreate, table=True):
    """
    This class creates the database
    """
    member_id: Optional[int] = Field(default=None, primary_key=True)
    password: int = Field(default=100)
    created_date: date = Field(default_factory=date.today)
    updated_date: date = Field(default_factory=date.today)

    staff: Optional["GymStaffsDB"] = Relationship(back_populates="member", cascade_delete=True)
    subscriptions: List["GymSubscriptionsDB"] = Relationship(back_populates="member", cascade_delete=True)

