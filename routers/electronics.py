from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel

router_electronics = APIRouter()


class GymElectronics(BaseModel):
    electro_id: int
    electro_name: str
    electro_count: int


electronic_items: list[GymElectronics] = []


@router_electronics.post("/electronics", status_code=status.HTTP_201_CREATED)
def add_electronics(electronic_item: GymElectronics) -> GymElectronics:
    """
    To add electronic items
    :param electronic_item:
    :return:
    """
    electronic_items.append(electronic_item)
    return electronic_item


@router_electronics.get('/electronics', status_code=status.HTTP_200_OK)
def list_electronics() -> list[GymElectronics]:
    """
    Fetches all electronic items
    :return: a list of all electronic items
    """
    return electronic_items


@router_electronics.get('/electronics/{electro_id}', status_code=status.HTTP_200_OK)
def get_electronics(electro_id: int) -> GymElectronics:
    """
    Fetches the details of the specific electronic item.
    :return: Details of the item specified
    """
    for el in electronic_items:
        if el.electro_id == electro_id:
            return el
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Electronics item:{electro_id} not found")
