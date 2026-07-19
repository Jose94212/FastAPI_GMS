from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException, Path
from sqlmodel import select

from database import SessionDep
from gms_assets.electronics.models import GymElectronics
from gms_assets.electronics.schemas import GymElectronicsCreate

router_electronics = APIRouter(prefix="/electronics",
                               tags=["Electronics"])


def _fetch_item_details(electro_id: Annotated[int, Path(title="The ID of gym electronics", ge=0)],
                        db_session: SessionDep) -> GymElectronics:
    """
    Fetches the details of a single item.
    :param electro_id: ID of the electronic item.
    :param db_session: DB session.
    :return: Details of the item.
    """
    item = db_session.get(GymElectronics, electro_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Electronics item:{electro_id} not found")
    return item


@router_electronics.post("/", status_code=status.HTTP_201_CREATED)
def add_electronics(electronic_item: GymElectronicsCreate,
                    db_session: SessionDep) -> GymElectronics:
    """
    Adds electronic items.
    :param db_session:
    :param electronic_item:
    :return:
    """
    db_item = GymElectronics.model_validate(electronic_item)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item


@router_electronics.get('/{electro_id}', status_code=status.HTTP_200_OK)
def get_electronics(electro_item: GymElectronics = Depends(_fetch_item_details)) -> GymElectronics:
    """
    Fetches the details of the specific electronic item.
    :param electro_item:
    :return: Details of the item specified
    """
    return electro_item


@router_electronics.get('/', status_code=status.HTTP_200_OK)
def list_electronics(db_session: SessionDep) -> Sequence[GymElectronics]:
    """
    Fetches all electronic items
    :return: a list of all electronic items
    """
    return db_session.exec(select(GymElectronics)).all()


@router_electronics.delete('/{electro_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_electronics(db_session: SessionDep,
                       existing_item: GymElectronics = Depends(_fetch_item_details),
                       ) -> None:
    """
    Deletes the specific electronic item.
    :return: Nothing
    """
    db_session.delete(existing_item)
    db_session.commit()
    return


@router_electronics.put('/{electro_id}', status_code=status.HTTP_200_OK)
def update_electronics(db_session: SessionDep,
                       updated_item: GymElectronicsCreate,
                       existing_item: GymElectronics = Depends(_fetch_item_details),
                       ) -> GymElectronics:
    """

    :param updated_item:
    :param existing_item:
    :param db_session:
    :return:
    """
    existing_item.electro_name = updated_item.electro_name
    existing_item.electro_count = updated_item.electro_count
    existing_item.electro_description = updated_item.electro_description
    db_session.add(existing_item)
    db_session.commit()
    db_session.refresh(existing_item)
    return existing_item
