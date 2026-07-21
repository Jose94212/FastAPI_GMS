from collections.abc import Sequence
from typing import Annotated

import bcrypt
from fastapi import APIRouter, status, Depends, HTTPException, Query, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from auth import create_access_token
from database import SessionDep
from gms_assets.users.models import UserProfile
from gms_assets.users.schemas import UserProfileCreate, UserProfileResponse

router_users = APIRouter(tags=["Users"],
                         prefix="/users")


def _fetch_item_details(user_id: Annotated[int, Path(title="The ID of the user", ge=0)],
                        db_session: SessionDep) -> UserProfile:
    """
    Fetches the details of a single user.
    :param user_id: ID of the user.
    :param db_session: DB session.
    :return: Details of the user.
    """
    item = db_session.get(UserProfile, user_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User id:{user_id} not found")
    return item


@router_users.post("/", status_code=status.HTTP_201_CREATED, response_model=UserProfileResponse)
def add_user(user: UserProfileCreate, db_session: SessionDep) -> UserProfile:
    """
    Adds a new user.
    :param user: Details of the user to add.
    :param db_session: DB session.
    :return: The added user, including their DB-assigned id.
    """
    user.password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    db_item = UserProfile.model_validate(user)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item


@router_users.get("/", response_model=list[UserProfileResponse], status_code=status.HTTP_200_OK)
def list_users(db_session: SessionDep,
               skip: int = Query(default=0, ge=0),
               limit: int = Query(default=25, ge=1, le=100)) -> Sequence[UserProfile]:
    """
    Lists users, paginated. Response is restricted to non-sensitive fields.
    :param skip: Number of users to skip.
    :param limit: Max number of users to return.
    :param db_session: DB session.
    :return: A page of users.
    """
    return db_session.exec(select(UserProfile).offset(skip).limit(limit)).all()


@router_users.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user(user_item: UserProfile = Depends(_fetch_item_details)) -> UserProfile:
    """
    Fetches the details of a specific user.
    :param user_item: Resolved user, from the dependency.
    :return: User details.
    """
    return user_item


@router_users.put("/{user_id}", status_code=status.HTTP_200_OK)
def update_user(db_session: SessionDep,
                updated_user: UserProfileCreate,
                existing_user: UserProfile = Depends(_fetch_item_details)) -> UserProfile:
    """
    Updates the details of an existing user.
    :param updated_user: New details to apply.
    :param existing_user: Resolved existing user, from the dependency.
    :param db_session: DB session.
    :return: Updated user.
    """
    existing_user.name = updated_user.name
    existing_user.email_id = updated_user.email_id
    existing_user.age = updated_user.age
    existing_user.position = updated_user.position
    existing_user.gender = updated_user.gender
    existing_user.contact_number = updated_user.contact_number
    existing_user.emergency_contact_number = updated_user.emergency_contact_number
    existing_user.blood_group = updated_user.blood_group
    db_session.add(existing_user)
    db_session.commit()
    db_session.refresh(existing_user)
    return existing_user


@router_users.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db_session: SessionDep,
                existing_user: UserProfile = Depends(_fetch_item_details)) -> None:
    """
    Deletes a specific user.
    :param existing_user: Resolved existing user, from the dependency.
    :param db_session: DB session.
    :return: Nothing.
    """
    db_session.delete(existing_user)
    db_session.commit()
    return


@router_users.post("/token", status_code=status.HTTP_200_OK)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db_session: SessionDep):
    """

    :param form_data:
    :param db_session:
    """
    user_details = db_session.exec(select(UserProfile).where(UserProfile.email_id == form_data.username)).first()
    if not user_details:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    else:
        if bcrypt.checkpw(form_data.password.encode("utf-8"), user_details.password.encode("utf-8")):
            data = {"sub": str(user_details.user_id)}
            token = create_access_token(data=data)
            return {"access_token": token,
                    "token_type": "bearer"}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
