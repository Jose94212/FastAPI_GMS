from datetime import datetime, timezone, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from database import SessionDep
from gms_assets.members.models import GymMembersDB
from gms_assets.members.schemas import GymRoles

# from gms_assets.users.models import UserProfileDB
# from gms_assets.users.schemas import UserTitle

SECRET_KEY = "JOSE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    """
    Creates JWT token
    :param data:
    :return:
    """
    data_copy = data.copy()
    data_copy["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(data_copy, SECRET_KEY, algorithm=ALGORITHM)


# 1. Point this to the endpoint URL where users get their token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


def get_current_user(db_session: SessionDep,
                     token: str = Depends(oauth2_scheme)) -> GymMembersDB:
    """
    Fetches the current user details
    :param db_session: DB session
    :param token: Token
    :return: User Profile
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},
                                          )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    else:
        user_profile = db_session.get(GymMembersDB, int(user_id))
        if user_profile:
            return user_profile
        else:
            raise credentials_exception


def require_owner(current_user: Annotated[GymMembersDB, Depends(get_current_user)]):
    """
    Checks whether the user is Owner or not
    :param current_user:
    :return:
    """
    if current_user.role != GymRoles.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner privileges required")
    return current_user
