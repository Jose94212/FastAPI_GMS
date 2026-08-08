from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from gms_assets.locker.schemas import GymLockerCreate

if TYPE_CHECKING:
    from gms_assets.members.models import GymMembersDB
    from gms_assets.staff.model import GymStaffsDB


class GymLockerDB(GymLockerCreate, table=True):
    """

    """
    locker_id: Optional[int] = Field(default=None, primary_key=True)
    staff_id: Optional[int] = Field(foreign_key="gymstaffsdb.staff_id", unique=True)
    member_id: Optional[int] = Field(foreign_key="gymmembersdb.member_id", unique=True)
    member: Optional["GymMembersDB"] = Relationship(back_populates="locker")
    staff: Optional["GymStaffsDB"] = Relationship(back_populates="locker")
