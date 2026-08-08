"""
Endpoints for the Staff resource. No auth dependency on these routes yet.
"""
import logging
from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, status, Depends
from sqlmodel import select

from auth import hash_password
from database import SessionDep
from gms_assets.members.models import GymMembersDB
from gms_assets.members.schemas import GymMemberStaffCommonDetails, GymRoles
from gms_assets.staff.model import GymStaffsDB
from gms_assets.staff.schemas import GymStaffsCreateRequest, GymStaffsUpdate

logger = logging.getLogger(__name__)

router_staff = APIRouter(tags=["Staff"],
                         prefix="/staff")


def _fetch_staff_details(staff_id: Annotated[int, Path(title="The ID of the member", ge=0)],
                         db_session: SessionDep) -> GymStaffsDB:
    """
    Fetches the details of a single user.
    :param staff_id: ID of the user.
    :param db_session: DB session.
    :return: Details of the user.
    """
    item = db_session.get(GymStaffsDB, staff_id)
    if item is None:
        logger.warning(f"Staff not found: {staff_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Staff id:{staff_id} not found")
    return item


@router_staff.post("", status_code=status.HTTP_201_CREATED)
def add_staff(staff: GymStaffsCreateRequest, db_session: SessionDep) -> GymStaffsDB:
    """
    Adds a new staff member. Also creates the linked Member row (staff are always
    members too) - see GymStaffsCreateRequest for why password lives on the request
    body but not on GymStaffsDB itself.
    :param staff: Details of the staff member to add, including their login password.
    :param db_session: DB session.
    :return: The added staff record, including its DB-assigned id and linked member_id.
    """
    common = GymMemberStaffCommonDetails.model_validate(staff)
    new_member = GymMembersDB(**common.model_dump(), role=GymRoles.member,
                              password=hash_password(staff.password))
    db_session.add(new_member)
    db_session.flush()  # assigns new_member.member_id, same transaction

    db_item = GymStaffsDB.model_validate(staff, update={"member_id": new_member.member_id})
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    logger.info(f"Staff created: {db_item.staff_id}")
    return db_item


@router_staff.get("", status_code=status.HTTP_200_OK)
def list_staff(db_session: SessionDep):
    """
    List all staff members.
    :param db_session: DB session.
    :return: All staff records.
    """
    return db_session.exec(select(GymStaffsDB)).all()


@router_staff.get("/{staff_id}", status_code=status.HTTP_200_OK)
def get_staff(member_details: GymStaffsDB = Depends(_fetch_staff_details)) -> GymStaffsDB:
    """
    Fetch the details of a specific staff member.
    :param member_details: Resolved staff record, from the dependency.
    :return: Details of the staff member.
    """
    return member_details


@router_staff.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(db_session: SessionDep,
                 staff_id: GymStaffsDB = Depends(_fetch_staff_details)) -> None:
    """
    Deletes the mentioned staff.

    Args:
        :db_session: Session of the DB
        :staff_id: Member ID to delete

    Returns:

    """
    member = db_session.get(GymMembersDB, staff_id.member_id)
    logger.info(f"Staff deleted: {staff_id.staff_id} (cascades to member {staff_id.member_id} and their subscriptions)")
    db_session.delete(member)  # cascades to the staff row and all subscriptions
    db_session.commit()
    return


@router_staff.patch("/{staff_id}", status_code=status.HTTP_200_OK)
def update_staff(updated_staff_details: GymStaffsUpdate,
                 db_session: SessionDep,
                 existing_staff: GymStaffsDB = Depends(_fetch_staff_details)):
    """
    Updates an existing staff record with partial data.

    Args:
        updated_staff_details: Fields to change (unset fields are left alone).
        db_session: DB session.
        existing_staff: The staff row resolved from the path id.

    Returns:
        The updated staff record.
    """
    updates = updated_staff_details.model_dump(exclude_unset=True)  # # converts to dict

    for k, v in updates.items():
        setattr(existing_staff, k, v)
    db_session.add(existing_staff)
    db_session.commit()
    db_session.refresh(existing_staff)
    logger.info(f"Staff updated: {existing_staff.staff_id}")
    return existing_staff
