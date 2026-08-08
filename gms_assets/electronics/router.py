"""
Endpoints for the Electronics resource (gym-owned electronics inventory).
All routes require a logged-in member; delete additionally requires the owner role.
"""
import logging
from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException, Path
from sqlmodel import select

from auth import get_current_user, require_owner
from database import SessionDep
from gms_assets.electronics.models import GymElectronicsDB
from gms_assets.electronics.schemas import GymElectronicsCreate
from gms_assets.members.models import GymMembersDB

logger = logging.getLogger(__name__)

router_electronics = APIRouter(prefix="/electronics",
                               dependencies=[Depends(get_current_user)],
                               tags=["Electronics"])


def _fetch_item_details(electro_id: Annotated[int, Path(title="The ID of gym electronics", ge=0)],
                        db_session: SessionDep) -> GymElectronicsDB:
    """
    Fetches the details of a single item.
    :param electro_id: ID of the electronic item.
    :param db_session: DB session.
    :return: Details of the item.
    """
    item = db_session.get(GymElectronicsDB, electro_id)
    if item is None:
        logger.warning(f"Electronics item not found: {electro_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Electronics item:{electro_id} not found")
    return item


@router_electronics.post("", status_code=status.HTTP_201_CREATED)
def add_electronics(electronic_item: GymElectronicsCreate,
                    db_session: SessionDep) -> GymElectronicsDB:
    """
    Adds electronic items.
    :param db_session:
    :param electronic_item:
    :return:
    """
    db_item = GymElectronicsDB.model_validate(electronic_item)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    logger.info(f"Electronics item created: {db_item.electro_id}")
    return db_item


@router_electronics.get('/{electro_id}', status_code=status.HTTP_200_OK)
def get_electronics(electro_item: GymElectronicsDB = Depends(_fetch_item_details)) -> GymElectronicsDB:
    """
    Fetches the details of the specific electronic item.
    :param electro_item:
    :return: Details of the item specified
    """
    return electro_item


@router_electronics.get("", status_code=status.HTTP_200_OK)
def list_electronics(db_session: SessionDep) -> Sequence[GymElectronicsDB]:
    """
    Fetches all electronic items
    :return: a list of all electronic items
    """
    return db_session.exec(select(GymElectronicsDB)).all()


@router_electronics.delete('/{electro_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_electronics(db_session: SessionDep,
                       existing_item: GymElectronicsDB = Depends(_fetch_item_details),
                       _: Annotated[GymMembersDB, Depends(require_owner)] = None) -> None:
    """
    Deletes the specific electronic item.
    :return: Nothing
    """
    logger.info(f"Electronics item deleted: {existing_item.electro_id}")
    db_session.delete(existing_item)
    db_session.commit()
    return


@router_electronics.put('/{electro_id}', status_code=status.HTTP_200_OK)
def update_electronics(db_session: SessionDep,
                       updated_item: GymElectronicsCreate,
                       existing_item: GymElectronicsDB = Depends(_fetch_item_details),
                       ) -> GymElectronicsDB:
    """
    Replaces the details of an existing electronic item (full replacement - all fields required).
    :param updated_item: New details to apply.
    :param existing_item: Resolved existing item, from the dependency.
    :param db_session: DB session.
    :return: Updated electronics item.
    """
    existing_item.electro_name = updated_item.electro_name
    existing_item.electro_count = updated_item.electro_count
    existing_item.electro_description = updated_item.electro_description
    db_session.add(existing_item)
    db_session.commit()
    db_session.refresh(existing_item)
    logger.info(f"Electronics item updated: {existing_item.electro_id}")
    return existing_item
