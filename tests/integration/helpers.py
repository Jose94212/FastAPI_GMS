"""
Shared helpers for the integration test suite - mainly for getting an
authenticated bearer token, since electronics/furniture/equipment routes
require a logged-in member (and their delete routes require the owner role
specifically).
"""


def _member_payload(email, password, role):
    """
    A minimal valid GymMembersCreate body with a chosen role.
    """
    return {
        "f_name": "Test",
        "l_name": "User",
        "email": email,
        "phone": "9000000099",
        "dob": "1990-01-01",
        "gender": "male",
        "emergency_contact_name": "Contact",
        "emergency_contact_number": "9111111111",
        "blood_group": "O+",
        "password": password,
        "role": role,
    }


def auth_headers(client, email="auth.test@example.com", password="password123", role="member"):
    """
    Creates a member with the given role, logs in, and returns an
    Authorization header dict ready to pass as `headers=` on a request.
    """
    client.post("/members", json=_member_payload(email, password, role))
    login_response = client.post("/members/token", data={"username": email, "password": password})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
