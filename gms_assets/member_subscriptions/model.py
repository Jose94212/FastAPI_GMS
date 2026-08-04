from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from gms_assets.member_subscriptions.schemas import GymSubscriptionsCreate

if TYPE_CHECKING:
    from gms_assets.members.models import GymMembersDB


class GymSubscriptionsDB(GymSubscriptionsCreate, table=True):
    """

    """
    subscription_id: Optional[int] = Field(primary_key=True, default=None)
    record_created: date = Field(default_factory=date.today)

    member: Optional["GymMembersDB"] = Relationship(back_populates="subscriptions")
