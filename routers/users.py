from __future__ import annotations

from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel

router_users = APIRouter()


class UserProfile(BaseModel):
    name: str
    email_id: str
    age: int
    position: str
    user_id: int


all_users: list[UserProfile] = []


@router_users.post("/users", status_code=status.HTTP_201_CREATED)
def add_user(user: UserProfile) -> UserProfile:
    """
    Adds a new user
    :param user: Details of the user to be added.
    :return: Added user details
    """
    all_users.append(user)
    return user


@router_users.get("/users", status_code=status.HTTP_200_OK)
def list_users() -> list[UserProfile]:
    """
    List all users
    :return:
    """
    return all_users


@router_users.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_user(user_id: int) -> UserProfile:
    """
    List all users
    :return:
    """
    for usr in all_users:
        if usr.user_id == user_id:
            return usr
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User id:{user_id} not found")


@router_users.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> None:
    """
    Deletes the user_id
    :return: None
    """
    for usr in all_users:
        if usr.user_id == user_id:
            all_users.remove(usr)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User id:{user_id} not found")


@router_users.put("/users/{user_id}", status_code=status.HTTP_200_OK)
def update_user(user_id: int, user: UserProfile) -> UserProfile:
    """
    Updates the user details
    :return: Updated user details
    """
    if user_id != user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{user_id} in path-parameter and body "
                                                                            f"request({user.user_id}) is "
                                                                            f"not same")

    for index, usr in enumerate(all_users):
        if usr.user_id == user_id:
            all_users[index] = user
            return all_users[index]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User id:{user_id} not found")
