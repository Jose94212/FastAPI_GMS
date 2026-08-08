"""
DB model for the Staff resource.
"""
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from gms_assets.staff.schemas import GymStaffsCreate

if TYPE_CHECKING:
    from gms_assets.members.models import GymMembersDB
    from gms_assets.locker.models import GymLockerDB


class GymStaffsDB(GymStaffsCreate, table=True):
    """
    DB-table created as per this class. member_id is unique - one member can have at
    most one linked staff row. cascade_delete on the locker relationship means a staff
    member's assigned locker is deleted along with them.
    """
    staff_id: Optional[int] = Field(default=None, primary_key=True)
    member_id: int = Field(foreign_key="gymmembersdb.member_id", unique=True)
    member: Optional["GymMembersDB"] = Relationship(back_populates="staff")
    locker: Optional["GymLockerDB"] = Relationship(back_populates="staff", cascade_delete=True)
