"""
Unit tests for GymLockerCreate's orphan-check validator (gms_assets.locker.schemas).
No client, no DB, no HTTP - constructs the Pydantic model directly.
"""
import pytest
from pydantic import ValidationError

from gms_assets.locker.schemas import GymLockerCreate


def test_locker_with_no_owner_raises_validation_error():
    """
    Neither member_id nor staff_id given - check_locker_allocated should reject it.
    """
    with pytest.raises(ValidationError):
        GymLockerCreate(locker_size="small")


def test_locker_with_member_id_only_is_valid():
    """
    member_id alone is enough to satisfy the validator.
    """
    locker = GymLockerCreate(locker_size="small", member_id=1)
    assert locker.member_id == 1
    assert locker.staff_id is None


def test_locker_with_staff_id_only_is_valid():
    """
    staff_id alone is also enough - the rule is "at least one", not "member only".
    """
    locker = GymLockerCreate(locker_size="small", staff_id=1)
    assert locker.staff_id == 1
    assert locker.member_id is None


def test_locker_with_both_ids_is_valid():
    """
    Having both is allowed too - the validator only rejects "neither".
    """
    locker = GymLockerCreate(locker_size="small", member_id=1, staff_id=2)
    assert locker.member_id == 1
    assert locker.staff_id == 2
