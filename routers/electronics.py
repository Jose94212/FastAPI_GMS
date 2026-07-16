from __future__ import annotations

from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, Field

router_electronics = APIRouter()


class GymElectronics(BaseModel):
    electro_id: int = Field(description="Unique item id")
    electro_name: str = Field(description="Name of the electronic item", examples=["Fan"], max_length=100)
    electro_description: str | None = Field(default=None, description="A short description of the item",
                                            max_length=200)
    electro_count: int = Field(description="Number of items", gt=0)


all_gym_electronics: list[GymElectronics] = []


def _fetch_item_details(electro_id: int) -> GymElectronics:
    """
    Iterates through the list of GymElectronics objects and returns the details of the matching item id.
    :param electro_id: Item's id
    :return: Details of the matched item id.
    """
    for el in all_gym_electronics:
        if el.electro_id == electro_id:
            return el
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Electronics item:{electro_id} not found")


@router_electronics.post("/electronics", status_code=status.HTTP_201_CREATED)
def add_electronics(electronic_item: GymElectronics) -> GymElectronics:
    """
    To add electronic items
    :param electronic_item:
    :return:
    """
    all_gym_electronics.append(electronic_item)
    return electronic_item


@router_electronics.get('/electronics', status_code=status.HTTP_200_OK)
def list_electronics() -> list[GymElectronics]:
    """
    Fetches all electronic items
    :return: a list of all electronic items
    """
    return all_gym_electronics


@router_electronics.get('/electronics/{electro_id}', status_code=status.HTTP_200_OK)
def get_electronics(electro_item: GymElectronics = Depends(_fetch_item_details)) -> GymElectronics:
    """
    Fetches the details of the specific electronic item.
    :param electro_item:
    :return: Details of the item specified
    """
    return electro_item


@router_electronics.put('/electronics/{electro_id}', status_code=status.HTTP_200_OK)
def put_electronics(electro_id: int,
                    electronic_item: GymElectronics,
                    available_items: GymElectronics = Depends(_fetch_item_details)) -> GymElectronics:
    """
    Updates the details of the electronic item as per id given.
    :param available_items: Object of the class
    :param electronic_item: all parameters of the electronic item
    :param electro_id: ID
    :return: Updated details
    """
    if electronic_item.electro_id != electro_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{electro_id} in path-parameter and body "
                                                                            f"request({electronic_item.electro_id}) is "
                                                                            f"not same")
    index = all_gym_electronics.index(available_items)
    all_gym_electronics[index] = electronic_item
    return all_gym_electronics[index]


@router_electronics.delete('/electronics/{electro_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_electronics(electro_item: GymElectronics = Depends(_fetch_item_details)) -> None:
    """
    Deletes the specific electronic item.
    :return: Nothing
    """
    all_gym_electronics.remove(electro_item)
    return
