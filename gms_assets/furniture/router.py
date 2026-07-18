from collections.abc import Sequence

from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select

from database import get_db_session
from gms_assets.furniture.models import FurnitureDetails
from gms_assets.furniture.schemas import FurnitureDetailsCreate

router_furniture = APIRouter(tags=["Furniture"])


def _fetch_item_details(fur_id: int, db_session: Session = Depends(get_db_session)) -> FurnitureDetails:
    """
    Fetches the details of a single furniture item.
    :param fur_id: ID of the furniture item.
    :param db_session: DB session.
    :return: Details of the item.
    """
    item = db_session.get(FurnitureDetails, fur_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Furniture item:{fur_id} not found")
    return item


@router_furniture.post("/furniture", status_code=status.HTTP_201_CREATED)
def add_furniture(furniture: FurnitureDetailsCreate,
                  db_session: Session = Depends(get_db_session)) -> FurnitureDetails:
    """
    Adds a new furniture item.
    :param furniture: Details of the furniture to add.
    :param db_session: DB session.
    :return: The added furniture item, including its DB-assigned id.
    """
    db_item = FurnitureDetails.model_validate(furniture)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item


@router_furniture.get('/furniture', status_code=status.HTTP_200_OK)
def list_furniture(db_session: Session = Depends(get_db_session)) -> Sequence[FurnitureDetails]:
    """
    Lists all furniture available in the gym.
    :param db_session: DB session.
    :return: All furniture items.
    """
    return db_session.exec(select(FurnitureDetails)).all()


@router_furniture.get('/furniture/{fur_id}', status_code=status.HTTP_200_OK)
def get_furniture(fur_item: FurnitureDetails = Depends(_fetch_item_details)) -> FurnitureDetails:
    """
    Fetches the details of a specific furniture item.
    :param fur_item: Resolved furniture item, from the dependency.
    :return: Details of the item.
    """
    return fur_item


@router_furniture.put('/furniture/{fur_id}', status_code=status.HTTP_200_OK)
def update_furniture(updated_item: FurnitureDetailsCreate,
                     existing_item: FurnitureDetails = Depends(_fetch_item_details),
                     db_session: Session = Depends(get_db_session)) -> FurnitureDetails:
    """
    Updates the details of an existing furniture item.
    :param updated_item: New details to apply.
    :param existing_item: Resolved existing item, from the dependency.
    :param db_session: DB session.
    :return: Updated furniture item.
    """
    existing_item.fur_name = updated_item.fur_name
    existing_item.fur_description = updated_item.fur_description
    existing_item.fur_count = updated_item.fur_count
    db_session.add(existing_item)
    db_session.commit()
    db_session.refresh(existing_item)
    return existing_item


@router_furniture.delete('/furniture/{fur_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_furniture(existing_item: FurnitureDetails = Depends(_fetch_item_details),
                     db_session: Session = Depends(get_db_session)) -> None:
    """
    Deletes a specific furniture item.
    :param existing_item: Resolved existing item, from the dependency.
    :param db_session: DB session.
    :return: Nothing.
    """
    db_session.delete(existing_item)
    db_session.commit()
    return
