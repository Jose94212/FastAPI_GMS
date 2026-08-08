"""
Endpoints for the Gym Equipment resource (weights, cardio machines, etc).
All routes require a logged-in member; delete additionally requires the owner role.
"""
import logging
from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException, Path
from sqlmodel import select

from auth import get_current_user, require_owner
from database import SessionDep
from gms_assets.equipment.models import GymEquipmentDB
from gms_assets.equipment.schemas import GymEquipmentCreate
from gms_assets.members.models import GymMembersDB

logger = logging.getLogger(__name__)

router_equipment = APIRouter(tags=["Equipment"],
                             dependencies=[Depends(get_current_user)],
                             prefix="/gym_equipment")


def _fetch_item_details(equip_id: Annotated[int, Path(title="The ID of gym equipment", ge=0)],
                        db_session: SessionDep) -> GymEquipmentDB:
    """
    Fetches the details of a single gym equipment item.
    :param equip_id: ID of the equipment item.
    :param db_session: DB session.
    :return: Details of the item.
    """
    item = db_session.get(GymEquipmentDB, equip_id)
    if item is None:
        logger.warning(f"Gym-equipment item not found: {equip_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gym-equipment item:{equip_id} not found")
    return item


@router_equipment.post("", status_code=status.HTTP_201_CREATED)
def add_equipment(gym_equip: GymEquipmentCreate, db_session: SessionDep) -> GymEquipmentDB:
    """
    Adds a new gym equipment item.
    :param gym_equip: Details of the equipment to add.
    :param db_session: DB session.
    :return: The added equipment item, including its DB-assigned id.
    """
    db_item = GymEquipmentDB.model_validate(gym_equip)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    logger.info(f"Gym-equipment item created: {db_item.equip_id}")
    return db_item


@router_equipment.get("", summary="Lists all gym equipment available", status_code=status.HTTP_200_OK)
def list_gym_equipment(db_session: SessionDep) -> Sequence[GymEquipmentDB]:
    """
    Fetches all gym equipment details.
    :param db_session: DB session.
    :return: All equipment items.
    """
    return db_session.exec(select(GymEquipmentDB)).all()


@router_equipment.get("/{equip_id}", status_code=status.HTTP_200_OK)
def get_gym_equipment(equip_item: GymEquipmentDB = Depends(_fetch_item_details)) -> GymEquipmentDB:
    """
    Fetches the details of a specific gym equipment item.
    :param equip_item: Resolved equipment item, from the dependency.
    :return: Details of the item.
    """
    return equip_item


@router_equipment.put('/{equip_id}', status_code=status.HTTP_200_OK)
def update_equipment(db_session: SessionDep,
                     updated_item: GymEquipmentCreate,
                     existing_item: GymEquipmentDB = Depends(_fetch_item_details),
                     ) -> GymEquipmentDB:
    """
    Updates the details of an existing gym equipment item.
    :param updated_item: New details to apply.
    :param existing_item: Resolved existing item, from the dependency.
    :param db_session: DB session.
    :return: Updated equipment item.
    """
    existing_item.equip_name = updated_item.equip_name
    existing_item.equip_description = updated_item.equip_description
    existing_item.equip_count = updated_item.equip_count
    existing_item.equip_lease = updated_item.equip_lease
    db_session.add(existing_item)
    db_session.commit()
    db_session.refresh(existing_item)
    logger.info(f"Gym-equipment item updated: {existing_item.equip_id}")
    return existing_item


@router_equipment.delete("/{equip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gym_equipment(db_session: SessionDep,
                         existing_item: GymEquipmentDB = Depends(_fetch_item_details),
                         _: Annotated[GymMembersDB, Depends(require_owner)] = None) -> None:
    """
    Deletes a specific gym equipment item.
    :param _:
    :param existing_item: Resolved existing item, from the dependency.
    :param db_session: DB session.
    :return: Nothing.
    """
    logger.info(f"Gym-equipment item deleted: {existing_item.equip_id}")
    db_session.delete(existing_item)
    db_session.commit()
    return
