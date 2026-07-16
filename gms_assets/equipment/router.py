from __future__ import annotations

from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, Field

router_equipment = APIRouter(tags=["Equipments"])


class GymEquipment(BaseModel):
    equip_id: int = Field(description="Unique id of the equipment")
    equip_name: str = Field(description="Name of the equipment", max_length=100)
    equip_description: str | None = Field(description="A short description about the equipment", max_length=1000,
                                          default=None)
    equip_count: int = Field(gt=0, description="Number of the items present")
    equip_lease: bool = Field(default=False, description="Equipment is on lease or not")


all_gym_equipments: list[GymEquipment] = []


def _get_item(equip_id: int) -> GymEquipment:
    """

    :param equip_id:
    :return:
    """
    for equip in all_gym_equipments:
        if equip.equip_id == equip_id:
            return equip
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gym-equipment item:{equip_id} not found")


@router_equipment.post('/gym_equipment', status_code=status.HTTP_201_CREATED)
def add_equipments(gym_equip: GymEquipment) -> GymEquipment:
    """
    method is to add gym equipments
    :param gym_equip:
    :return:
    """
    all_gym_equipments.append(gym_equip)
    return gym_equip


@router_equipment.get("/gym_equipment", summary="Lists all gym equipment available", status_code=status.HTTP_200_OK)
def list_gym_equipment() -> list[GymEquipment]:
    """
    Fetches all gym equipments details
    :return: list of all gym equipments
    """
    return all_gym_equipments


@router_equipment.delete("/gym_equipment/{equip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gym_equipment(equip_id_details: GymEquipment = Depends(_get_item)) -> None:
    """
    Deletes the specific gym equipment details
    :return:
    """
    all_gym_equipments.remove(equip_id_details)


@router_equipment.put('/gym_equipment/{equip_id}', status_code=status.HTTP_200_OK)
def update_equipment(equip_id: int,
                     gym_equip: GymEquipment,
                     available_gym_equip_details: GymEquipment = Depends(_get_item)) -> GymEquipment:
    """
    Updates the equipment.
    :param available_gym_equip_details:
    :param equip_id: ID of the equipments
    :param gym_equip:
    :return: Updated details
    """
    if gym_equip.equip_id != equip_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{equip_id} in path-parameter and body "
                                                                            f"request({gym_equip.equip_id}) is "
                                                                            f"not same")
    index = all_gym_equipments.index(available_gym_equip_details)
    all_gym_equipments[index] = gym_equip
    return all_gym_equipments[index]


@router_equipment.get("/gym_equipment/{equip_id}", status_code=status.HTTP_200_OK)
def get_gym_equipment(gym_equip_id_details: GymEquipment = Depends(_get_item)) -> GymEquipment:
    """
    Fetches the equipment details
    :return: details of the specific equipment.
    """
    return gym_equip_id_details
