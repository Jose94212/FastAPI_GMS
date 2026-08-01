from typing import Annotated

from fastapi import APIRouter, status, Path, HTTPException, Depends
from sqlmodel import select

from database import SessionDep
from gms_assets.members.models import GymMembersDB, GymStaffsDB
from gms_assets.members.schemas import GymMembersCreate, GymMembersUpdate, GymRoles, GymStaffsCreate, GymStaffsUpdate

router_member = APIRouter(tags=["Members"],
                          prefix="/members")


def _fetch_member_details(member_id: Annotated[int, Path(title="The ID of the member", ge=0)],
                          db_session: SessionDep) -> GymMembersDB:
    """
    Fetches the details of a single user.
    :param member_id: ID of the user.
    :param db_session: DB session.
    :return: Details of the user.
    """
    item = db_session.get(GymMembersDB, member_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member id:{member_id} not found")
    return item


@router_member.post("", status_code=status.HTTP_201_CREATED)
def add_member(member: GymStaffsCreate, db_session: SessionDep) -> GymMembersDB:
    """

    :param db_session:
    :param member:
    """
    db_item = GymMembersDB.model_validate(member)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)

    if member.role != GymRoles.member:
        staff_item = GymStaffsDB(member_id=db_item.member_id, salary=member.salary, hire_date=member.hired_date)
        db_session.add(staff_item)
        db_session.commit()
        db_session.refresh(db_item)
    return db_item


@router_member.get("", status_code=status.HTTP_200_OK)
def list_members(db_session: SessionDep):
    """
    List all members.
    :param db_session:
    """
    return db_session.exec(select(GymMembersDB)).all()


@router_member.get("/{member_id}", status_code=status.HTTP_200_OK)
def get_member(member_details: GymMembersDB = Depends(_fetch_member_details)) -> GymMembersDB:
    """
    Fetch the details of the member.
    :param member_details: ID of the member
    :return:
    """
    return member_details


@router_member.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(db_session: SessionDep,
                  member_id: GymMembersDB = Depends(_fetch_member_details)) -> None:
    """
    Deletes the member.
    :param db_session: Session of the DB
    :param member_id: Member ID to delete
    """
    db_session.delete(member_id)
    db_session.commit()
    return


@router_member.patch("/{member_id}", status_code=status.HTTP_200_OK)
def update_member(update_member_data: GymMembersUpdate,
                  db_session: SessionDep,
                  existing_member_data: GymMembersDB = Depends(_fetch_member_details)):
    """

    :param update_member_data:
    :param db_session:
    :param existing_member_data:
    """
    updates = update_member_data.model_dump(exclude_unset=True)  # # converts to dict

    for k, v in updates.items():
        setattr(existing_member_data, k, v)
    db_session.add(existing_member_data)
    db_session.commit()
    db_session.refresh(existing_member_data)
    return existing_member_data


@router_member.patch("/{staff_id}", status_code=status.HTTP_200_OK)
def update_staff(updated_staff_details: GymStaffsUpdate,
                 db_session: SessionDep,
                 existing_staff: GymStaffsDB = Depends(_fetch_member_details)):
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
    return existing_staff
