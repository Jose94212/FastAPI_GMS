from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import EmailStr, model_validator
from sqlmodel import SQLModel, Field


class Gender(str, Enum):
    """
    This class specifies the gender.
    """
    male = "male"
    female = "female"
    others = "others"


class MemberStatus(str, Enum):
    """
    Status of the gym membership
    """
    active = "active"
    frozen = "frozen"
    cancel = "canceled"


class GymRoles(str, Enum):
    """
    Gym roles
    """
    member = "member"
    trainer = "trainer"
    receptionist = "receptionist"
    dietitian = "dietitian"
    owner = "owner"


class GymMembersCreate(SQLModel):
    """
    Member details
    """
    f_name: str = Field(max_length=50)
    l_name: str = Field(max_length=50)
    email: EmailStr = Field(max_length=100, unique=True)
    phone: str = Field(max_length=10)
    dob: date = Field(description="Format: YYYY-MM-DD")
    gender: Gender = Field(description="Format: male/female/others")
    emergency_contact_name: str = Field(max_length=50)
    emergency_contact_number: str = Field(max_length=10)
    joining_date: date = Field(default_factory=date.today,
                               description="Format: YYYY-MM-DD. Defaults to today's date if left blank.")
    member_status: MemberStatus = Field(default=MemberStatus.active)
    blood_group: str = Field(description="Blood group of the member")
    role: GymRoles | None = Field(default=GymRoles.member)


class GymStaffsCreate(GymMembersCreate):
    """
    Staff details
    """
    hired_date: date | None = None
    salary: int | None = None

    @model_validator(mode="after")
    def check_staff_fields(self):
        """
        Validation for role field
        :return:
        """
        if self.role != GymRoles.member and (self.salary is None or self.hired_date is None):
            raise ValueError("salary and hired_date are required when role is not 'member'")
        return self


class GymMembersUpdate(SQLModel):
    """
    Updates the details of members.
    """
    f_name: str | None = None
    l_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    dob: date | None = None
    gender: Gender | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    joining_date: date | None = None
    member_status: MemberStatus | None = None
    blood_group: str | None = None
    role: GymRoles | None = Field(default=GymRoles.member)


class GymStaffsUpdate(GymMembersUpdate):
    salary: int | None = None
    hired_date: date | None = None
