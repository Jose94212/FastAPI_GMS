from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, status, Depends
from sqlmodel import select

from database import SessionDep
from gms_assets.locker.models import GymLockerDB
from gms_assets.locker.schemas import GymLockerCreate, GymLockerUpdate

router_locker = APIRouter(tags=["Locker"],
                          prefix="/locker")


def _fetch_locker_details(locker_id: Annotated[int, Path(title="The ID of the locker", ge=0)],
                          db_session: SessionDep) -> GymLockerDB:
    """
    Fetches the details of a single locker.
    :param locker_id: ID of the locker.
    :param db_session: DB session.
    :return: Details of the locker.
    """
    item = db_session.get(GymLockerDB, locker_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Locker id:{locker_id} not found")
    return item


@router_locker.post("", status_code=status.HTTP_201_CREATED)
def add_locker(locker: GymLockerCreate, db_session: SessionDep) -> GymLockerDB:
    """
    Adds a new locker, allocated to a member or staff.
    :param locker:
    :param db_session:
    :return:
    """
    db_item = GymLockerDB.model_validate(locker)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item


@router_locker.get("", status_code=status.HTTP_200_OK)
def list_lockers(db_session: SessionDep) -> list[GymLockerDB]:
    """
    List all lockers.
    :param db_session:
    """
    return db_session.exec(select(GymLockerDB)).all()


@router_locker.get("/{locker_id}", status_code=status.HTTP_200_OK)
def get_locker(locker_details: GymLockerDB = Depends(_fetch_locker_details)) -> GymLockerDB:
    """
    Fetch the details of the locker.
    :param locker_details: ID of the locker
    :return:
    """
    return locker_details


@router_locker.delete("/{locker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_locker(db_session: SessionDep,
                  existing_locker: GymLockerDB = Depends(_fetch_locker_details)) -> None:
    """
    Deletes the mentioned locker.

    Args:
        db_session: Session of the DB
        existing_locker: The locker row resolved from the path id.
    """
    db_session.delete(existing_locker)
    db_session.commit()
    return


@router_locker.patch("/{locker_id}", status_code=status.HTTP_200_OK)
def update_locker(updated_locker_details: GymLockerUpdate,
                  db_session: SessionDep,
                  existing_locker: GymLockerDB = Depends(_fetch_locker_details)) -> GymLockerDB:
    """
    Updates an existing locker record with partial data.

    Args:
        updated_locker_details: Fields to change (unset fields are left alone).
        db_session: DB session.
        existing_locker: The locker row resolved from the path id.

    Returns:
        The updated locker record.
    """
    updates = updated_locker_details.model_dump(exclude_unset=True)

    for k, v in updates.items():
        setattr(existing_locker, k, v)

    if not existing_locker.member_id and not existing_locker.staff_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Locker should be allocated to a member or staff")

    db_session.add(existing_locker)
    db_session.commit()
    db_session.refresh(existing_locker)
    return existing_locker
