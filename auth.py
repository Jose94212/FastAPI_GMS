"""
Authentication and authorization: password hashing, JWT issuing/decoding, and the
FastAPI dependencies (get_current_user, require_owner) used to protect routes.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from database import SessionDep
from gms_assets.members.models import GymMembersDB
from gms_assets.members.schemas import GymRoles

import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(plain_password: str) -> str:
    """
    Hashes a plain-text password for storage.
    :param plain_password:
    :return: bcrypt hash, as a string
    """
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks a plain-text password against a stored bcrypt hash.
    :param plain_password:
    :param hashed_password:
    :return: True if it matches
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/members/token")


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
                                          headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        logger.warning(f"Token validation failed: {e}")
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        logger.warning("Token missing 'sub' claim")
        raise credentials_exception
    else:
        user_profile = db_session.get(GymMembersDB, int(user_id))
        if user_profile:
            # DEBUG, not INFO: this runs on every single authenticated request,
            # not just discrete business events, so INFO would flood the logs.
            logger.debug(f"Authenticated user: {user_profile.member_id}")
            return user_profile
        else:
            logger.warning(f"Token valid but member no longer exists: {user_id}")
            raise credentials_exception


def require_owner(current_user: Annotated[GymMembersDB, Depends(get_current_user)]):
    """
    Checks whether the user is Owner or not
    :param current_user:
    :return:
    """
    if current_user.role != GymRoles.owner:
        logger.warning(f"Owner-only action denied for member: {current_user.member_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner privileges required")
    return current_user
