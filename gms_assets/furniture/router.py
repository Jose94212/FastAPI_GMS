from __future__ import annotations

from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, Field

router_furniture = APIRouter(tags=["Furniture"])


class FurnitureDetails(BaseModel):
    fur_id: int = Field(description="Unique id of the furniture")
    fur_name: str = Field(description="Name of the furniture", max_length=100, examples=["sofa or office-desk"])
    fur_description: str | None = Field(description="A short description of the furniture", max_length=200,
                                        default=None)
    fur_count: int = Field(description="Number of items", ge=0)


all_gym_furniture: list[FurnitureDetails] = []


def _get_item(fur_id: int) -> FurnitureDetails:
    """
    Fetches the details of the specified furniture id.
    :param fur_id: ID of the furniture.
    :return: Details of the furniture.
    """
    for i in all_gym_furniture:
        if i.fur_id == fur_id:
            return i
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Furniture item:{fur_id} not found")


@router_furniture.post("/furniture", status_code=status.HTTP_201_CREATED)
def add_furniture(furniture: FurnitureDetails) -> FurnitureDetails:
    """
    This method adds information about the furniture
    :param furniture: Details of the furniture
    :return: Added furniture details
    """
    all_gym_furniture.append(furniture)
    return furniture


@router_furniture.get('/furniture', status_code=status.HTTP_200_OK)
def list_furniture() -> list[FurnitureDetails]:
    """
    Lists all furniture available in the gym.
    :return: Furniture details
    """
    return all_gym_furniture


@router_furniture.get('/furniture/{fur_id}', status_code=status.HTTP_200_OK)
def get_furniture(fur_items: FurnitureDetails = Depends(_get_item)) -> FurnitureDetails:
    """
    Fetch the furniture details
    :return: specific furniture details
    """
    return fur_items


@router_furniture.delete('/furniture/{fur_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_furniture(fur_items: FurnitureDetails = Depends(_get_item)) -> None:
    """
    Deletes the furniture details
    :return:
    """
    all_gym_furniture.remove(fur_items)
    return


@router_furniture.put('/furniture/{fur_id}', status_code=status.HTTP_200_OK)
def update_furniture(fur_id: int,
                     update_furniture_item: FurnitureDetails,
                     available_furniture: FurnitureDetails = Depends(_get_item)) -> FurnitureDetails:
    """
    Updates the furniture details
    :return: Updated furniture details
    """
    if update_furniture_item.fur_id != fur_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{fur_id} in path-parameter and body "
                                   f"request({update_furniture_item.fur_id}) is not same")

    index = all_gym_furniture.index(available_furniture)
    all_gym_furniture[index] = update_furniture_item
    return all_gym_furniture[index]
