from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel

router_equipments = APIRouter()


class GymEquipments(BaseModel):
    equip_id: int
    equip_name: str
    equip_count: int
    equip_lease: bool


all_gym_equipments: list[GymEquipments] = []


@router_equipments.post('/gym_equipments', status_code=status.HTTP_201_CREATED)
def add_equipments(gym_equip: GymEquipments) -> GymEquipments:
    """
    method is to add gym equipments
    :param gym_equip:
    :return:
    """
    all_gym_equipments.append(gym_equip)
    return gym_equip


@router_equipments.get("/gym_equipments", status_code=status.HTTP_200_OK)
def list_gym_equipments() -> list[GymEquipments]:
    """
    Fetches all gym equipments details
    :return: list of all gym equipments
    """
    return all_gym_equipments


@router_equipments.delete("/gym_equipments/{equip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gym_equipment(equip_id: int) -> None:
    """
    Deletes the specific gym equipment details
    :return:
    """
    for equip in all_gym_equipments:
        if equip.equip_id == equip_id:
            all_gym_equipments.remove(equip)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gym-equipment item:{equip_id} not found")


@router_equipments.put('/gym_equipments/{equip_id}', status_code=status.HTTP_200_OK)
def update_equipments(equip_id: int, gym_equip: GymEquipments) -> GymEquipments:
    """
    Updates the equipments
    :param equip_id: ID of the equipments
    :param gym_equip:
    :return: Updated details
    """
    if gym_equip.equip_id != equip_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{equip_id} in path-parameter and body "
                                                                            f"request({gym_equip.equip_id}) is "
                                                                            f"not same")

    for index, el in enumerate(all_gym_equipments):
        if el.equip_id == equip_id:
            all_gym_equipments[index] = gym_equip
            return all_gym_equipments[index]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gym-equipment item:{equip_id} not found")


@router_equipments.get("/gym_equipments/{gym_equip_id}", status_code=status.HTTP_200_OK)
def get_gym_equipment(gym_equip_id: int) -> GymEquipments:
    """
    Fetches the equipment details
    :return: details of the specific equipment.
    """
    for equip in all_gym_equipments:
        if equip.equip_id == gym_equip_id:
            return equip
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gym-equipment item:{gym_equip_id} not found")
