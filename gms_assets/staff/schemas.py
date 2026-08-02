from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from gms_assets.members.schemas import GymMemberStaffCommonDetails, Gender


class GymStaffRoles(str, Enum):
    """

    """
    staff_trainer = "trainer"
    staff_receptionist = "receptionist"
    staff_dietitian = "dietitian"


class GymStaffStatus(str, Enum):
    """

    """
    active = "active"
    hold = "hold"
    resigned = "resigned"


class GymStaffsCreate(GymMemberStaffCommonDetails):
    """
    Staff details
    """
    hired_date: date | None = Field(default_factory=date.today)
    salary: int | None = Field(default=10000)
    role: GymStaffRoles | None = Field(default=GymStaffRoles.staff_trainer)
    status: GymStaffStatus | None = Field(default=GymStaffStatus.active)


class GymStaffsUpdate(SQLModel):
    """

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
