from __future__ import annotations

from sqlmodel import Field

from gms_assets.staff.schemas import GymStaffsCreate


class GymStaffsDB(GymStaffsCreate, table=True):
    """

    """
    staff_id: int | None = Field(default=None, primary_key=True)
    # member_id: int = Field(foreign_key="gymmembersdb.member_id", unique=True)
