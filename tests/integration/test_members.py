"""
Tests for the Members resource and login (gms_assets.members) - creation,
password hashing/no-leak, and the /members/token login flow.
"""


def _member_payload(email="test.user@example.com", password="password123"):
    """
    A minimal valid GymMembersCreate body, reused across tests.
    """
    return {
        "f_name": "Test",
        "l_name": "User",
        "email": email,
        "phone": "9000000001",
        "dob": "1990-01-01",
        "gender": "male",
        "emergency_contact_name": "Contact",
        "emergency_contact_number": "9111111111",
        "blood_group": "O+",
        "password": password,
    }


def test_create_member_hides_password(client):
    """
    POST /members should 201 and the response should never include the
    password or password hash (GymMembersResponse has no password field).
    """
    response = client.post("/members", json=_member_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "test.user@example.com"
    assert "password" not in body


def test_create_member_defaults_role_to_member(client):
    """
    A member created without an explicit role should default to "member".
    """
    response = client.post("/members", json=_member_payload())
    assert response.json()["role"] == "member"


def test_login_with_correct_password_succeeds(client):
    """
    Logging in with the same password used at signup should return a bearer token.
    """
    client.post("/members", json=_member_payload(email="login.ok@example.com", password="password123"))

    response = client.post("/members/token", data={
        "username": "login.ok@example.com",
        "password": "password123",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_fails(client):
    """
    Wrong password should 401, not leak whether the email exists.
    """
    client.post("/members", json=_member_payload(email="login.bad@example.com", password="password123"))

    response = client.post("/members/token", data={
        "username": "login.bad@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_login_with_nonexistent_email_fails_the_same_way(client):
    """
    A nonexistent email should fail with the same status/detail as a wrong
    password - anti-enumeration, verified by comparing the two responses.
    """
    client.post("/members", json=_member_payload(email="login.bad2@example.com", password="password123"))

    wrong_password = client.post("/members/token", data={
        "username": "login.bad2@example.com",
        "password": "wrongpassword",
    })
    nonexistent_email = client.post("/members/token", data={
        "username": "nobody@example.com",
        "password": "wrongpassword",
    })

    assert wrong_password.status_code == nonexistent_email.status_code == 401
    assert wrong_password.json()["detail"] == nonexistent_email.json()["detail"]
