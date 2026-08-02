from __future__ import annotations

from datetime import date

from sqlmodel import Field

from gms_assets.members.schemas import GymMembersCreate


class GymMembersDB(GymMembersCreate, table=True):
    """
    This class creates the database
    """
    member_id: int | None = Field(default=None, primary_key=True)
    password: int = Field(default=100)
    created_date: date = Field(default_factory=date.today)
    updated_date: date = Field(default_factory=date.today)


