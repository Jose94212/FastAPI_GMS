from __future__ import annotations

from enum import Enum

from fastapi import APIRouter, status, HTTPException, Query, Depends
from pydantic import BaseModel, Field

router_users = APIRouter()


class _Gender(str, Enum):
    """
    This class specifies about the gender
    """
    male = "male"
    female = "female"


class _UserTitle(str, Enum):
    """
    User specifications
    """
    owner = "owner"
    trainer = "trainer"
    member = "member"


class UserProfile(BaseModel):
    name: str = Field(description="Name of the user", max_length=100)
    email_id: str = Field(description="Email id of the user", max_length=190)
    age: int = Field(description="Age of the user", gt=14)
    position: _UserTitle = Field(description="Position of the user", examples=["owner", "trainer", "member"],
                                 default="member")
    user_id: int = Field(description="Unique id of the user", gt=0)
    gender: _Gender = Field(description="Sex of the person, in small letters", examples=["male", "female"])
    contact_number: str = Field(description="Personal number to contact")
    emergency_contact_number: str = Field(description="A contact-number other than personal which can be used for "
                                                      "emergencies")
    blood_group: str = Field(description="Blood group of the person")


class UserProfileResponse(BaseModel):
    name: str = Field(description="Name of the user", max_length=100)
    position: _UserTitle = Field(description="Position of the user", examples=["owner", "trainer", "member"],
                                 default="member")
    user_id: int = Field(description="Unique id of the user", gt=0)
    gender: _Gender = Field(description="Sex of the person, in small letters", examples=["male", "female"])


all_users: list[UserProfile] = []


def _get_item(user_id: int) -> UserProfile:
    """
    Fetches the details of the user id.
    :param user_id: ID of the user.
    :return: User details.
    """
    for usr in all_users:
        if usr.user_id == user_id:
            return usr
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User id:{user_id} not found")


@router_users.post("/users", status_code=status.HTTP_201_CREATED)
def add_user(user: UserProfile) -> UserProfile:
    """
    Adds a new user
    :param user: Details of the user to be added.
    :return: Added user details
    """
    all_users.append(user)
    return user


@router_users.get("/users", response_model=list[UserProfileResponse], status_code=status.HTTP_200_OK)
def list_users(skip: int = Query(default=0, ge=0), limit: int = Query(default=25, ge=1, le=100)) -> list[UserProfile]:
    """
    List all users
    :return:
    """
    return all_users[skip:skip + limit]


@router_users.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_user(user_items: UserProfile = Depends(_get_item)) -> UserProfile:
    """
    Fetches the details of the user.
    :return: User details.
    """
    return user_items


@router_users.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_items: UserProfile = Depends(_get_item)) -> None:
    """
    Deletes the user_id
    :return: None
    """
    all_users.remove(user_items)


@router_users.put("/users/{user_id}", status_code=status.HTTP_200_OK)
def update_user(user_id: int,
                user_update: UserProfile,
                user_details: UserProfile = Depends(_get_item)) -> UserProfile:
    """
    Updates the user details
    :return: Updated user details
    """
    if user_id != user_update.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{user_id} in path-parameter and body "
                                                                            f"request({user_update.user_id}) is "
                                                                            f"not same")
    index = all_users.index(user_details)
    all_users[index] = user_update
    return all_users[index]
