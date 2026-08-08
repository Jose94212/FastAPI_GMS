"""
Shared pytest fixtures for the whole test suite. Anything defined here is
automatically visible to every test file under tests/, no import needed.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine
from sqlmodel import SQLModel
from database import get_db_session
from main import gms


@pytest.fixture(name="client")
def client_fixture():
    """
    Spins up a fresh in-memory SQLite DB per test, swaps it in for the real
    database via dependency_overrides, and hands the test a TestClient wired
    to that fake DB. Nothing here ever touches the real gms.db.
    """
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)

    def override_get_db_session():
        with Session(test_engine) as session:
            yield session

    gms.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(gms) as test_client:
        yield test_client

    gms.dependency_overrides.clear()
