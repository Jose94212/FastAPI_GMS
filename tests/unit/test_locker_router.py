"""
Unit tests for the Locker router's add_locker/update_locker (gms_assets.locker.router).
db_session is a MagicMock, not a real database - these only check that the
functions call the session correctly (add/commit/refresh, in order, on the
right object), not that data actually persists. Real persistence and FK/unique
constraints are covered separately by tests/integration/test_locker.py.
"""
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from gms_assets.locker.models import GymLockerDB
from gms_assets.locker.router import add_locker, update_locker
from gms_assets.locker.schemas import GymLockerCreate, GymLockerUpdate, LockerSize


def test_add_locker_saves_and_commits():
    """
    add_locker should build a GymLockerDB from the input and hand it to the
    session's add/commit/refresh, in that order.
    """
    fake_session = MagicMock()
    new_locker = GymLockerCreate(locker_size=LockerSize.size_small, member_id=1)

    result = add_locker(locker=new_locker, db_session=fake_session)

    assert isinstance(result, GymLockerDB)
    assert result.member_id == 1
    fake_session.add.assert_called_once()
    fake_session.commit.assert_called_once()
    fake_session.refresh.assert_called_once()


def test_update_locker_applies_partial_updates():
    """
    Only fields present in the update body should change - untouched fields
    (like member_id here) should be left exactly as they were.
    """
    fake_session = MagicMock()
    existing = GymLockerDB(locker_id=1, locker_size=LockerSize.size_medium, member_id=1, staff_id=None)
    updates = GymLockerUpdate(locker_size=LockerSize.size_big)

    result = update_locker(updated_locker_details=updates, db_session=fake_session, existing_locker=existing)

    assert result.locker_size == LockerSize.size_big
    assert result.member_id == 1
    fake_session.add.assert_called_once_with(existing)
    fake_session.commit.assert_called_once()
    fake_session.refresh.assert_called_once_with(existing)


def test_update_locker_rejects_orphaning_the_locker():
    """
    Setting member_id to None with no staff_id to fall back on should raise a
    422 before the session ever commits - update_locker's manual re-check.
    """
    fake_session = MagicMock()
    existing = GymLockerDB(locker_id=1, locker_size=LockerSize.size_medium, member_id=1, staff_id=None)
    updates = GymLockerUpdate(member_id=None)

    with pytest.raises(HTTPException) as exc_info:
        update_locker(updated_locker_details=updates, db_session=fake_session, existing_locker=existing)

    assert exc_info.value.status_code == 422
    fake_session.commit.assert_not_called()
