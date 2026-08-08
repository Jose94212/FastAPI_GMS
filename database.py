"""
Database engine and session setup, shared by every resource in the app.
"""
from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, Session, SQLModel

engine = create_engine("sqlite:///./gms.db")


def create_db_and_tables():
    """
    Creates every table registered on SQLModel's metadata (i.e. every imported
    *DB model) if it doesn't already exist. Called once at app startup, in main.py's
    lifespan handler.
    """
    SQLModel.metadata.create_all(engine)


def get_db_session():
    """
    Fetches the current session and passes the same.
    """
    with Session(engine) as db_session:
        yield db_session


SessionDep = Annotated[Session, Depends(get_db_session)]
