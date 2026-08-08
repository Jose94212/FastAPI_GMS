"""
Endpoints for the Members resource, plus login (POST /members/token). No auth
dependency on the CRUD routes here yet - only /token issues/checks credentials.
"""
import logging
from typing import Annotated

from fastapi import APIRouter, status, Path, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from auth import create_access_token, hash_password, verify_password
from database import SessionDep
from gms_assets.members.models import GymMembersDB
from gms_assets.members.schemas import GymMembersCreate, GymMembersUpdate, GymMembersListResponse, GymMembersResponse

logger = logging.getLogger(__name__)

router_member = APIRouter(tags=["Members"],
                          prefix="/members")


def _fetch_member_details(member_id: Annotated[int, Path(title="The ID of the member", ge=0)],
                          db_session: SessionDep) -> GymMembersDB:
    """
    Fetches the details of a single user.
    :param member_id: ID of the user.
    :param db_session: DB session.
    :return: Details of the user.
    """
    item = db_session.get(GymMembersDB, member_id)
    if item is None:
        logger.warning(f"Member not found: {member_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member id:{member_id} not found")
    return item


@router_member.post("", status_code=status.HTTP_201_CREATED)
def add_member(member: GymMembersCreate, db_session: SessionDep) -> GymMembersResponse:
    """
    Adds a plain member. To add staff (which also creates the linked member row),
    use POST /staff instead.
    :param db_session:
    :param member:
    """
    db_item = GymMembersDB.model_validate(member, update={"password": hash_password(member.password)})
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    logger.info(f"Member created: {db_item.member_id}")
    return db_item


@router_member.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db_session: SessionDep) -> dict:
    """
    Logs a member in using their email (as username) and password, returns a JWT access token.
    :param form_data: OAuth2 form - form_data.username is the member's email.
    :param db_session:
    """
    login_failed = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail="Incorrect email or password",
                                 headers={"WWW-Authenticate": "Bearer"})

    member = db_session.exec(select(GymMembersDB).where(GymMembersDB.email == form_data.username)).first()
    # Same error for "no such email" and "wrong password" - avoids leaking which emails are registered.
    if not member or not verify_password(form_data.password, member.password):
        logger.warning(f"Failed login attempt for: {form_data.username}")
        raise login_failed

    logger.info(f"Successful login: {member.member_id}")
    access_token = create_access_token({"sub": str(member.member_id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router_member.get("", response_model=list[GymMembersListResponse], status_code=status.HTTP_200_OK)
def list_members(db_session: SessionDep):
    """
    List all members.
    :param db_session:
    """
    return db_session.exec(select(GymMembersDB)).all()


@router_member.get("/{member_id}", status_code=status.HTTP_200_OK)
def get_member(member_details: GymMembersDB = Depends(_fetch_member_details)) -> GymMembersResponse:
    """
    Fetch the details of the member.
    :param member_details: ID of the member
    :return:
    """
    return member_details


@router_member.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(db_session: SessionDep,
                  member_id: GymMembersDB = Depends(_fetch_member_details)) -> None:
    """
    Deletes the member.
    :param db_session: Session of the DB
    :param member_id: Member ID to delete
    """
    logger.info(f"Member deleted: {member_id.member_id}")
    db_session.delete(member_id)
    db_session.commit()
    return


@router_member.patch("/{member_id}", status_code=status.HTTP_200_OK)
def update_member(update_member_data: GymMembersUpdate,
                  db_session: SessionDep,
                  existing_member_data: GymMembersDB = Depends(_fetch_member_details)) -> GymMembersResponse:
    """
    Updates an existing member record with partial data (unset fields are left alone).
    :param update_member_data: Fields to change.
    :param db_session: DB session.
    :param existing_member_data: The member row resolved from the path id.
    :return: The updated member record.
    """
    updates = update_member_data.model_dump(exclude_unset=True)  # # converts to dict

    for k, v in updates.items():
        setattr(existing_member_data, k, v)
    db_session.add(existing_member_data)
    db_session.commit()
    db_session.refresh(existing_member_data)
    logger.info(f"Member updated: {existing_member_data.member_id}")
    return existing_member_data
