from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException, Path
from sqlmodel import select

from database import SessionDep
from gms_assets.equipment.models import GymEquipment
from gms_assets.equipment.schemas import GymEquipmentCreate

router_equipment = APIRouter(tags=["Equipment"],
                             prefix="/gym_equipment")


def _fetch_item_details(equip_id: Annotated[int, Path(title="The ID of gym equipment", ge=0)],
                        db_session: SessionDep) -> GymEquipment:
    """
    Fetches the details of a single gym equipment item.
    :param equip_id: ID of the equipment item.
    :param db_session: DB session.
    :return: Details of the item.
    """
    item = db_session.get(GymEquipment, equip_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gym-equipment item:{equip_id} not found")
    return item


@router_equipment.post('/', status_code=status.HTTP_201_CREATED)
def add_equipment(gym_equip: GymEquipmentCreate, db_session: SessionDep) -> GymEquipment:
    """
    Adds a new gym equipment item.
    :param gym_equip: Details of the equipment to add.
    :param db_session: DB session.
    :return: The added equipment item, including its DB-assigned id.
    """
    db_item = GymEquipment.model_validate(gym_equip)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item


@router_equipment.get("/", summary="Lists all gym equipment available", status_code=status.HTTP_200_OK)
def list_gym_equipment(db_session: SessionDep) -> Sequence[GymEquipment]:
    """
    Fetches all gym equipment details.
    :param db_session: DB session.
    :return: All equipment items.
    """
    return db_session.exec(select(GymEquipment)).all()


@router_equipment.get("/{equip_id}", status_code=status.HTTP_200_OK)
def get_gym_equipment(equip_item: GymEquipment = Depends(_fetch_item_details)) -> GymEquipment:
    """
    Fetches the details of a specific gym equipment item.
    :param equip_item: Resolved equipment item, from the dependency.
    :return: Details of the item.
    """
    return equip_item


@router_equipment.put('/{equip_id}', status_code=status.HTTP_200_OK)
def update_equipment(db_session: SessionDep,
                     updated_item: GymEquipmentCreate,
                     existing_item: GymEquipment = Depends(_fetch_item_details),
                     ) -> GymEquipment:
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
    return existing_item


@router_equipment.delete("/{equip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gym_equipment(db_session: SessionDep,
                         existing_item: GymEquipment = Depends(_fetch_item_details),
                         ) -> None:
    """
    Deletes a specific gym equipment item.
    :param existing_item: Resolved existing item, from the dependency.
    :param db_session: DB session.
    :return: Nothing.
    """
    db_session.delete(existing_item)
    db_session.commit()
    return
