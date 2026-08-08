"""
Schemas for the Staff resource. Every staff member is also a Member - GymStaffsCreate
builds on GymMemberStaffCommonDetails (shared with gms_assets.members.schemas) so the
personal-details fields are defined exactly once, not duplicated.
"""
from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from gms_assets.members.schemas import GymMemberStaffCommonDetails, Gender


class GymStaffRoles(str, Enum):
    """
    Job role of a staff member.
    """
    staff_trainer = "trainer"
    staff_receptionist = "receptionist"
    staff_dietitian = "dietitian"


class GymStaffStatus(str, Enum):
    """
    Employment status of a staff member.
    """
    active = "active"
    hold = "hold"
    resigned = "resigned"


class GymStaffsCreate(GymMemberStaffCommonDetails):
    """
    Staff details. Note: no password field here - GymStaffsDB inherits directly from this
    class, and a staff row's login credentials live only on its linked Member row, not
    duplicated onto the staff table. See GymStaffsCreateRequest for the actual POST /staff body.
    """
    hired_date: date | None = Field(default_factory=date.today)
    salary: int | None = Field(default=10000)
    role: GymStaffRoles | None = Field(default=GymStaffRoles.staff_trainer)
    status: GymStaffStatus | None = Field(default=GymStaffStatus.active)


class GymStaffsCreateRequest(GymStaffsCreate):
    """
    Request body for POST /staff. Adds the plain-text login password on top of
    GymStaffsCreate, without it becoming a column on GymStaffsDB.
    """
    password: str = Field(min_length=6, description="Plain-text login password (hashed before storage).")


class GymStaffsUpdate(SQLModel):
    """
    Updates the details of a staff record. All fields optional/None-default so
    PATCH can send only the fields being changed.
    """
    f_name: str | None = Field(max_length=50, default=None)
    l_name: str | None = Field(max_length=50, default=None)
    email: EmailStr | None = Field(max_length=100, unique=True, default=None)
    phone: str | None = Field(max_length=10, default=None)
    dob: date | None = Field(description="Format: YYYY-MM-DD", default=None)
    gender: Gender | None = Field(description="Format: male/female/others", default=None)
    emergency_contact_name: str | None = Field(max_length=50, default=None)
    emergency_contact_number: str | None = Field(max_length=10, default=None)
    blood_group: str | None = Field(description="Blood group of the member", default=None)
    salary: int | None = None
    hired_date: date | None = None
    role: GymStaffRoles | None = Field(default=GymStaffRoles.staff_trainer)
    status: GymStaffStatus | None = Field(default=GymStaffStatus.active)
