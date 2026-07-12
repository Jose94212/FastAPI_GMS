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


@router_electronics.put('/electronics/{electro_id}', status_code=status.HTTP_200_OK)
def put_electronics(electro_id: int, electronic_item: GymElectronics) -> GymElectronics:
    """
    Updates the details of the electronic item as per id given
    :param electronic_item: all parameters of the electronic item
    :param electro_id: ID
    :return: Updated details
    """
    if electronic_item.electro_id != electro_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{electro_id} in path-parameter and body "
                                                                            f"request({electronic_item.electro_id}) is "
                                                                            f"not same")

    for index, el in enumerate(electronic_items):
        if el.electro_id == electro_id:
            electronic_items[index] = electronic_item
            return electronic_items[index]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Electronics item:{electro_id} not found")


@router_electronics.delete('/electronics/{electro_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_electronics(electro_id: int) -> None:
    """
    Deletes the specific electronic item.
    :return: Nothing
    """
    for el in electronic_items:
        if el.electro_id == electro_id:
            electronic_items.remove(el)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Electronics item_id:{electro_id} not found")
