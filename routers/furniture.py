from __future__ import annotations

from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field

router_furniture = APIRouter()


class FurnitureDetails(BaseModel):
    fur_id: int = Field(description="Unique id of the furniture")
    fur_name: str = Field(description="Name of the furniture", max_length=100, examples=["sofa or office-desk"])
    fur_description: str | None = Field(description="A short description of the furniture", max_length=200,
                                        default=None)
    fur_count: int = Field(gt=0, description="Number of items")


all_furniture: list[FurnitureDetails] = []


@router_furniture.post("/furniture", status_code=status.HTTP_201_CREATED)
def add_furniture(furniture: FurnitureDetails) -> FurnitureDetails:
    """
    This method adds information about the furniture
    :param furniture: Details of the furniture
    :return: Added furniture details
    """
    all_furniture.append(furniture)
    return furniture


@router_furniture.get('/furniture', status_code=status.HTTP_200_OK)
def list_furniture() -> list[FurnitureDetails]:
    """
    Lists all furniture available in the gym.
    :return: Furniture details
    """
    return all_furniture


@router_furniture.get('/furniture/{fur_id}', status_code=status.HTTP_200_OK)
def get_furniture(fur_id: int) -> FurnitureDetails:
    """
    Fetch the furniture details
    :return: specific furniture details
    """
    for i in all_furniture:
        if i.fur_id == fur_id:
            return i
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Furniture item:{fur_id} not found")


@router_furniture.delete('/furniture/{fur_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_furniture(fur_id: int) -> None:
    """
    Deletes the furniture details
    :return:
    """
    for i in all_furniture:
        if i.fur_id == fur_id:
            all_furniture.remove(i)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Furniture item:{fur_id} not found")


@router_furniture.put('/furniture/{fur_id}', status_code=status.HTTP_200_OK)
def update_furniture(fur_id: int, furniture: FurnitureDetails) -> FurnitureDetails:
    """
    Updates the furniture details
    :return: Updated furniture details
    """
    if furniture.fur_id != fur_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{fur_id} in path-parameter and body "
                                                                            f"request({furniture.fur_id}) is "
                                                                            f"not same")

    for index, value in enumerate(all_furniture):
        if value.fur_id == fur_id:
            all_furniture[index] = furniture
            return all_furniture[index]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Furniture item:{fur_id} not found")
