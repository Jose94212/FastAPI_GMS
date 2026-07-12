from fastapi import APIRouter, status
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
