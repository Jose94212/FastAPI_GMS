"""
Tests for the Staff resource (gms_assets.staff) - specifically the "staff is also
a member" behavior: POST /staff creates a linked Member row too, and deleting a
staff member cascades to delete that Member row (via Relationship cascade_delete).
"""


def _staff_payload(email="staff.test@example.com", password="password123"):
    """
    A minimal valid GymStaffsCreateRequest body, reused across tests.
    """
    return {
        "f_name": "Staff",
        "l_name": "Person",
        "email": email,
        "phone": "9000000002",
        "dob": "1992-01-01",
        "gender": "female",
        "emergency_contact_name": "Contact",
        "emergency_contact_number": "9111111111",
        "blood_group": "A+",
        "password": password,
    }


def test_create_staff_also_creates_linked_member(client):
    """
    POST /staff should 201 and return a staff row with a member_id pointing at
    a real, fetchable Member row.
    """
    response = client.post("/staff", json=_staff_payload())
    assert response.status_code == 201
    staff = response.json()
    assert staff["member_id"] is not None

    member_response = client.get(f"/members/{staff['member_id']}")
    assert member_response.status_code == 200
    assert member_response.json()["email"] == "staff.test@example.com"


def test_deleting_staff_cascades_to_linked_member(client):
    """
    DELETE /staff/{id} deletes the GymMembersDB row via cascade_delete, since
    add_staff/delete_staff operate on the member row, not the staff row directly.
    """
    staff = client.post("/staff", json=_staff_payload(email="cascade.test@example.com")).json()
    member_id = staff["member_id"]

    delete_response = client.delete(f"/staff/{staff['staff_id']}")
    assert delete_response.status_code == 204

    member_response = client.get(f"/members/{member_id}")
    assert member_response.status_code == 404


def test_staff_login_uses_linked_member_password(client):
    """
    A staff member logs in through /members/token using the password they
    signed up with - staff credentials live on the linked Member row.
    """
    client.post("/staff", json=_staff_payload(email="staff.login@example.com", password="staffpass123"))

    response = client.post("/members/token", data={
        "username": "staff.login@example.com",
        "password": "staffpass123",
    })
    assert response.status_code == 200
    assert response.json()["access_token"]
