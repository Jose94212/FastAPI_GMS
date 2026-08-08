"""
Tests for the Locker resource (gms_assets.locker) - the "must be allocated to a
member or staff, never neither" rule, and cascade delete when the owner is removed.
"""


def _create_member(client, email="locker.member@example.com"):
    """
    Creates a member via the API and returns its member_id.
    """
    response = client.post("/members",
                           json={
                               "f_name": "Locker",
                               "l_name": "Owner",
                               "email": email,
                               "phone": "9000000003",
                               "dob": "1991-01-01",
                               "gender": "male",
                               "emergency_contact_name": "Contact",
                               "emergency_contact_number": "9111111111",
                               "blood_group": "B+",
                               "password": "password123",
                           })
    return response.json()["member_id"]


def test_create_locker_with_no_owner_is_rejected(client):
    """
    A locker with neither member_id nor staff_id should fail validation
    (GymLockerCreate.check_locker_allocated) before it ever reaches the DB.
    """
    response = client.post("/locker", json={"locker_size": "small"})
    assert response.status_code == 422


def test_create_locker_for_member_succeeds(client):
    """
    A locker allocated to a real member_id should be created successfully.
    """
    member_id = _create_member(client)
    response = client.post("/locker",
                           json={"locker_size": "small", "member_id": member_id})
    assert response.status_code == 201
    assert response.json()["member_id"] == member_id


def test_update_locker_that_would_orphan_it_is_rejected(client):
    """
    PATCH-ing away the only owner (member_id) with no staff_id to replace it
    should be rejected by update_locker's manual re-check.
    """
    member_id = _create_member(client, email="locker.orphan@example.com")
    locker = client.post("/locker",
                         json={"locker_size": "medium", "member_id": member_id}).json()

    response = client.patch(f"/locker/{locker['locker_id']}", json={"member_id": None})
    assert response.status_code == 422


def test_deleting_member_cascades_to_their_locker(client):
    """
    Deleting a member should delete their locker too, via
    GymMembersDB.locker's cascade_delete=True.
    """
    member_id = _create_member(client, email="locker.cascade@example.com")
    locker = client.post("/locker", json={"locker_size": "big", "member_id": member_id}).json()

    delete_response = client.delete(f"/members/{member_id}")
    assert delete_response.status_code == 204

    locker_response = client.get(f"/locker/{locker['locker_id']}")
    assert locker_response.status_code == 404
