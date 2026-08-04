from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from gms_assets.staff.schemas import GymStaffsCreate

if TYPE_CHECKING:
    from gms_assets.members.models import GymMembersDB


class GymStaffsDB(GymStaffsCreate, table=True):
    """

    """
    staff_id: Optional[int] = Field(default=None, primary_key=True)
    member_id: int = Field(foreign_key="gymmembersdb.member_id", unique=True)
    member: Optional["GymMembersDB"] = Relationship(back_populates="staff")
