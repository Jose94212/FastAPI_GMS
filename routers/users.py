from __future__ import annotations

from fastapi import APIRouter, status
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
