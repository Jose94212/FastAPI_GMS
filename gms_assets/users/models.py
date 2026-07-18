"""
This module is related to Database.
Classes created in this will be used for creating tables with respective columns in the table.
"""
from __future__ import annotations

from sqlmodel import Field
from gms_assets.users.schemas import UserProfileCreate


class UserProfile(UserProfileCreate, table=True):
    """
    DB-table created as per this class.
    """
    user_id: int | None = Field(default=None, primary_key=True)
