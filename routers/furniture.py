from fastapi import APIRouter, status
from pydantic import BaseModel

router_furniture = APIRouter()


class FurnitureDetails(BaseModel):
    fur_id: int
    fur_name: str
    fur_count: int


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
