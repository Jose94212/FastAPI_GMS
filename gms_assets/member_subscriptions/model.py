from __future__ import annotations

from datetime import date

from sqlmodel import Field

from gms_assets.member_subscriptions.schemas import GymSubscriptionsCreate


class GymSubscriptionsDB(GymSubscriptionsCreate, table=True):
    """

    """
    subscription_id: int | None = Field(primary_key=True, default=None)
    record_created: date = Field(default_factory=date.today)

