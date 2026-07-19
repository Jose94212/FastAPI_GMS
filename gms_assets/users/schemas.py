"""
Schemas manage how data enters and exits your API via HTTP.
They validate incoming JSON requests, filter outgoing JSON responses,
and automatically generate your interactive Swagger/OpenAPI Documentation.

NOTE: inherited from SQLModel (not plain Pydantic BaseModel) so that
'models.py' can inherit these same fields instead of duplicating them.
"""
from __future__ import annotations

from enum import Enum

from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class Gender(str, Enum):
    """
    This class specifies the gender.
    """
    male = "male"
    female = "female"


class UserTitle(str, Enum):
    """
    User specifications.
    """
    owner = "owner"
    trainer = "trainer"
    member = "member"


class UserProfileCreate(SQLModel):
    """
    Details required for adding a new user. No id here - the DB assigns it.
    """
    name: str = Field(max_length=100)
    email_id: EmailStr = Field(max_length=190)
    age: int = Field(gt=14)
    position: UserTitle = Field(default=UserTitle.member)
    gender: Gender
    contact_number: str
    emergency_contact_number: str = Field(description="A contact-number other than personal which can be used for "
                                                      "emergencies")
    blood_group: str


class UserProfileResponse(SQLModel):
    """
    Restricted, public-safe view of a user - excludes PII (email, contact numbers, blood group).
    """
    user_id: int
    name: str
    position: UserTitle
    gender: Gender
