"""
Unit tests for the password hashing helpers in auth.py (gms_assets-wide,
used by both members and staff signup). Pure functions - no client, no DB.
"""
from auth import hash_password, verify_password


def test_hash_password_does_not_return_the_plain_text():
    """
    The stored value should never just be the original password.
    """
    hashed = hash_password("mypassword123")
    assert hashed != "mypassword123"


def test_hash_password_is_not_deterministic():
    """
    bcrypt salts each hash, so hashing the same password twice should give
    two different hashes.
    """
    first = hash_password("mypassword123")
    second = hash_password("mypassword123")
    assert first != second


def test_verify_password_accepts_the_correct_password():
    hashed = hash_password("mypassword123")
    assert verify_password("mypassword123", hashed) is True


def test_verify_password_rejects_the_wrong_password():
    hashed = hash_password("mypassword123")
    assert verify_password("wrongpassword", hashed) is False
