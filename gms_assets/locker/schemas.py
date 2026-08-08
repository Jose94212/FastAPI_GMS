"""
Schemas for the Locker resource. A locker must always be allocated to exactly a
member or a staff member (or both, via update) - never neither.
"""
from __future__ import annotations

from enum import Enum

from pydantic import model_validator
from sqlmodel import SQLModel, Field


class LockerSize(str, Enum):
    """
    Details of Locker size
    """
    size_big = "big"
    size_medium = "medium"
    size_small = "small"


class GymLockerCreate(SQLModel):
    """
    Details of locker
    """
    locker_size: LockerSize | None = Field(default=LockerSize.size_medium)
    member_id: int | None = Field(default=None)
    staff_id: int | None = Field(default=None)

    @model_validator(mode="after")
    def check_locker_allocated(self):
        """
        Check either member or staff ID is present (not both missing)
        """
        if not self.member_id and not self.staff_id:
            raise ValueError("Locker should be allocated to a member or staff")

        return self


class GymLockerUpdate(SQLModel):
    """
    Updates the details of a locker.
    """
    locker_size: LockerSize | None = None
    member_id: int | None = None
    staff_id: int | None = None

