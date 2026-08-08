"""
Endpoints for the Membership Plans resource. No auth dependency on these routes yet.
"""
import logging
from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends, Path
from sqlmodel import select

from database import SessionDep
from gms_assets.membership_plans.models import GymMembershipPlansDB
from gms_assets.membership_plans.schemas import GymMembershipPlansCreate

logger = logging.getLogger(__name__)

router_plans = APIRouter(tags=["Plans"],
                         prefix="/plans")


def _fetch_plan(plan_id: Annotated[int, Path(title="The ID of the plan", ge=0)],
                db_session: SessionDep) -> GymMembershipPlansDB:
    """
    Fetches the details of a single plan.
    :param plan_id: ID of the plan.
    :param db_session: DB session.
    :return: Details of the plan.
    """
    item = db_session.get(GymMembershipPlansDB, plan_id)
    if not item:
        logger.warning(f"Plan not found: {plan_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan id:{plan_id} not found")
    return item


@router_plans.post("", status_code=status.HTTP_201_CREATED)
def add_plan(new_plan: GymMembershipPlansCreate, db_session: SessionDep) -> GymMembershipPlansDB:
    """
    Adds a new membership plan.
    :param new_plan: Details of the plan to add.
    :param db_session: DB session.
    :return: The added plan, including its DB-assigned id.
    """
    db_item = GymMembershipPlansDB.model_validate(new_plan)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    logger.info(f"Plan created: {db_item.plan_id}")
    return db_item


@router_plans.get("", status_code=status.HTTP_200_OK)
def list_plans(db_session: SessionDep) -> Sequence[GymMembershipPlansDB]:
    """
    Lists all membership plans.
    :param db_session: DB session.
    :return: All plans.
    """
    return db_session.exec(select(GymMembershipPlansDB)).all()


@router_plans.get("/{plan_id}", status_code=status.HTTP_200_OK)
def get_plan(existing_plan: GymMembershipPlansDB = Depends(_fetch_plan)) -> GymMembershipPlansDB:
    """
    Fetches the details of a specific plan.
    :param existing_plan: Resolved plan, from the dependency.
    :return: Details of the plan.
    """
    return existing_plan


@router_plans.put("/{plan_id}", status_code=status.HTTP_200_OK)
def update_plan(updated_plan: GymMembershipPlansCreate,
                db_session: SessionDep,
                existing_plan: GymMembershipPlansDB = Depends(_fetch_plan)) -> GymMembershipPlansDB:
    """
    Replaces the details of an existing plan (full replacement - all fields required).
    :param updated_plan: New details to apply.
    :param db_session: DB session.
    :param existing_plan: Resolved plan, from the dependency.
    :return: Updated plan.
    """
    existing_plan.plan_name = updated_plan.plan_name
    existing_plan.price = updated_plan.price
    existing_plan.duration_months = updated_plan.duration_months
    db_session.add(existing_plan)
    db_session.commit()
    db_session.refresh(existing_plan)
    logger.info(f"Plan updated: {existing_plan.plan_id}")
    return existing_plan


@router_plans.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(db_session: SessionDep,
                existing_plan: GymMembershipPlansDB = Depends(_fetch_plan)) -> None:
    """
    Deletes a specific plan.
    :param db_session: DB session.
    :param existing_plan: Resolved plan, from the dependency.
    :return: Nothing.
    """
    logger.info(f"Plan deleted: {existing_plan.plan_id}")
    db_session.delete(existing_plan)
    db_session.commit()
    return
