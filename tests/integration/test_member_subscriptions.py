"""
Tests for the Member Subscriptions resource (gms_assets.member_subscriptions) -
links a Member to a Membership Plan. No auth dependency on these routes yet.
"""


def _create_member(client, email="sub.member@example.com"):
    """
    Creates a member via the API and returns its member_id.
    """
    response = client.post("/members", json={
        "f_name": "Sub",
        "l_name": "Scriber",
        "email": email,
        "phone": "9000000004",
        "dob": "1993-01-01",
        "gender": "female",
        "emergency_contact_name": "Contact",
        "emergency_contact_number": "9111111111",
        "blood_group": "AB+",
        "password": "password123",
    })
    return response.json()["member_id"]


def _create_plan(client):
    """
    Creates a membership plan via the API and returns its plan_id.
    """
    response = client.post("/plans", json={"plan_name": "Cardio", "price": 1000, "duration_months": 1})
    return response.json()["plan_id"]


def test_create_subscription(client):
    """
    POST /subscriptions should 201 given a valid member_id/plan_id pair.
    """
    member_id = _create_member(client)
    plan_id = _create_plan(client)

    response = client.post("/subscriptions", json={
        "member_id": member_id,
        "plan_id": plan_id,
        "start_date": "2026-01-01",
        "end_date": "2026-02-01",
    })
    assert response.status_code == 201
    body = response.json()
    assert body["member_id"] == member_id
    assert body["plan_id"] == plan_id
    assert body["status"] == "active"


def test_get_subscription_not_found(client):
    """
    GET /subscriptions/{id} for a subscription that doesn't exist should 404.
    """
    response = client.get("/subscriptions/999")
    assert response.status_code == 404


def test_list_subscriptions(client):
    """
    GET /subscriptions should include subscriptions created earlier in the same test.
    """
    member_id = _create_member(client, email="sub.list@example.com")
    plan_id = _create_plan(client)
    client.post("/subscriptions", json={
        "member_id": member_id, "plan_id": plan_id,
        "start_date": "2026-01-01", "end_date": "2026-02-01",
    })

    response = client.get("/subscriptions")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete_subscription(client):
    """
    DELETE /subscriptions/{id} should remove it - a follow-up GET then 404s.
    """
    member_id = _create_member(client, email="sub.delete@example.com")
    plan_id = _create_plan(client)
    sub = client.post("/subscriptions", json={
        "member_id": member_id, "plan_id": plan_id,
        "start_date": "2026-01-01", "end_date": "2026-02-01",
    }).json()

    delete_response = client.delete(f"/subscriptions/{sub['subscription_id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/subscriptions/{sub['subscription_id']}")
    assert get_response.status_code == 404


def test_deleting_member_cascades_to_their_subscriptions(client):
    """
    Deleting a member should delete their subscriptions too, via
    GymMembersDB.subscriptions' cascade_delete=True.
    """
    member_id = _create_member(client, email="sub.cascade@example.com")
    plan_id = _create_plan(client)
    sub = client.post("/subscriptions", json={
        "member_id": member_id, "plan_id": plan_id,
        "start_date": "2026-01-01", "end_date": "2026-02-01",
    }).json()

    delete_response = client.delete(f"/members/{member_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/subscriptions/{sub['subscription_id']}")
    assert get_response.status_code == 404
