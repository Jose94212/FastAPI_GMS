from __future__ import annotations

from datetime import date

from sqlmodel import Field, SQLModel

from gms_assets.members.schemas import GymMembersCreate


class GymMembersDB(GymMembersCreate, table=True):
    """
    This class creates the database
    """
    member_id: int | None = Field(default=None, primary_key=True)
    created_date: date = Field(default_factory=date.today)
    updated_date: date = Field(default_factory=date.today)


class GymStaffsDB(SQLModel, table=True):
    staff_id: int | None = Field(default=None, primary_key=True)
    member_id: int = Field(foreign_key="gymmembersdb.member_id", unique=True)
    salary: int = Field(default=10000)
    hire_date: date
