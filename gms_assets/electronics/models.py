"""
This module is related to Database.
Classes created in this will be used for creating tables with respective columns in the table.
"""
from __future__ import annotations

from sqlmodel import Field
from gms_assets.electronics.schemas import GymElectronicsCreate


class GymElectronicsDB(GymElectronicsCreate, table=True):
    """
    DB-table created as per this class.
    """
    electro_id: int | None = Field(default=None, primary_key=True)
