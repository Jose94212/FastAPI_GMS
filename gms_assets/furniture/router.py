from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException, Path
from sqlmodel import select

from auth import get_current_user, require_owner
from database import SessionDep
from gms_assets.furniture.models import FurnitureDB
from gms_assets.furniture.schemas import FurnitureDetailsCreate
from gms_assets.members.models import GymMembersDB

router_furniture = APIRouter(tags=["Furniture"],
                             dependencies=[Depends(get_current_user)],
                             prefix="/furniture")


def _fetch_item_details(fur_id: Annotated[int, Path(title="The ID of the furniture", ge=0)],
                        db_session: SessionDep) -> FurnitureDB:
    """
    Fetches the details of a single furniture item.
    :param fur_id: ID of the furniture item.
    :param db_session: DB session.
    :return: Details of the item.
    """
    item = db_session.get(FurnitureDB, fur_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Furniture item:{fur_id} not found")
    return item


@router_furniture.post("", status_code=status.HTTP_201_CREATED)
def add_furniture(db_session: SessionDep,
                  furniture: FurnitureDetailsCreate) -> FurnitureDB:
    """
    Adds a new furniture item.
    :param furniture: Details of the furniture to add.
    :param db_session: DB session.
    :return: The added furniture item, including its DB-assigned id.
    """
    db_item = FurnitureDB.model_validate(furniture)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item


@router_furniture.get('', status_code=status.HTTP_200_OK)
def list_furniture(db_session: SessionDep) -> Sequence[FurnitureDB]:
    """
    Lists all furniture available in the gym.
    :param db_session: DB session.
    :return: All furniture items.
    """
    return db_session.exec(select(FurnitureDB)).all()


@router_furniture.get('/{fur_id}', status_code=status.HTTP_200_OK)
def get_furniture(fur_item: FurnitureDB = Depends(_fetch_item_details)) -> FurnitureDB:
    """
    Fetches the details of a specific furniture item.
    :param fur_item: Resolved furniture item, from the dependency.
    :return: Details of the item.
    """
    return fur_item


@router_furniture.put('/{fur_id}', status_code=status.HTTP_200_OK)
def update_furniture(db_session: SessionDep,
                     updated_item: FurnitureDetailsCreate,
                     existing_item: FurnitureDB = Depends(_fetch_item_details)) -> FurnitureDB:
    """
    Updates the details of an existing furniture item.
    :param updated_item: New details to apply.
    :param existing_item: Resolved existing item from the dependency.
    :param db_session: DB session.
    :return: Updated furniture item.
    """
    existing_item.fur_name = updated_item.fur_name
    existing_item.fur_description = updated_item.fur_description
    existing_item.fur_count = updated_item.fur_count
    db_session.add(existing_item)
    db_session.commit()
    db_session.refresh(existing_item)
    return existing_item


@router_furniture.delete('/{fur_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_furniture(db_session: SessionDep,
                     existing_item: FurnitureDB = Depends(_fetch_item_details),
                     _: Annotated[GymMembersDB, Depends(require_owner)] = None
                     ) -> None:
    """
    Deletes a specific furniture item.
    :param _:
    :param existing_item: Resolved existing item, from the dependency.
    :param db_session: DB session.
    :return: Nothing.
    """
    db_session.delete(existing_item)
    db_session.commit()
    return
