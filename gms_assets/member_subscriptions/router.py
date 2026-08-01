from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends, Path
from sqlmodel import select

from database import SessionDep
from gms_assets.member_subscriptions.model import GymSubscriptionsDB
from gms_assets.member_subscriptions.schemas import GymSubscriptionsCreate

router_subscriptions = APIRouter(prefix="/subscriptions",
                                 tags=['Subscription'])


def _fetch_subscription(subscription_id: Annotated[int, Path(title="The ID of the subscription", ge=0)],
                        db_session: SessionDep) -> GymSubscriptionsDB:
    """
    Fetches the details of a single subscription.
    :param subscription_id: ID of the subscription.
    :param db_session: DB session.
    :return: Details of the subscription.
    """
    subscription_details = db_session.get(GymSubscriptionsDB, subscription_id)
    if not subscription_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscription id:{subscription_id} not found")
    return subscription_details


@router_subscriptions.post("", status_code=status.HTTP_201_CREATED)
def add_subscription(db_session: SessionDep,
                     new_sub: GymSubscriptionsCreate) -> GymSubscriptionsDB:
    """
    Adds a new subscription.
    :param db_session: DB session.
    :param new_sub: Details of the subscription to add.
    :return: The added subscription, including its DB-assigned id.
    """
    db_item = GymSubscriptionsDB.model_validate(new_sub)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item


@router_subscriptions.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(db_session: SessionDep,
                        existing_subscription: GymSubscriptionsDB = Depends(_fetch_subscription)) -> None:
    """
    Deletes a specific subscription.
    :param db_session: DB session.
    :param existing_subscription: Resolved subscription, from the dependency.
    :return: Nothing.
    """
    db_session.delete(existing_subscription)
    db_session.commit()
    return


@router_subscriptions.get("", status_code=status.HTTP_200_OK)
def list_subscriptions(db_session: SessionDep):
    """
    Lists all subscriptions.
    :param db_session: DB session.
    :return: All subscriptions.
    """
    return db_session.exec(select(GymSubscriptionsDB)).all()


@router_subscriptions.get("/{subscription_id}", status_code=status.HTTP_200_OK)
def get_subscription(existing_subscription: GymSubscriptionsDB = Depends(_fetch_subscription)) -> GymSubscriptionsDB:
    """
    Fetches the details of a specific subscription.
    :param existing_subscription: Resolved subscription, from the dependency.
    :return: Details of the subscription.
    """
    return existing_subscription
