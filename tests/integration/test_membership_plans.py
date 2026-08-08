"""
Tests for the Membership Plans resource (gms_assets.membership_plans).
"""


def test_create_plan(client):
    """
    POST /plans should return 201 and echo back the created plan with a plan_id.
    """
    response = client.post("/plans", json={
        "plan_name": "Cardio",
        "price": 1000,
        "duration_months": 1,
    })
    assert response.status_code == 201
    body = response.json()
    assert body["plan_name"] == "Cardio"
    assert body["plan_id"] is not None


def test_get_plan_not_found(client):
    """
    GET /plans/{id} for a plan that doesn't exist should 404.
    """
    response = client.get("/plans/999")
    assert response.status_code == 404


def test_list_plans_reflects_created_plans(client):
    """
    GET /plans should include plans created earlier in the same test.
    """
    client.post("/plans", json={"plan_name": "Yoga", "price": 1000, "duration_months": 1})
    response = client.get("/plans")
    assert response.status_code == 200
    names = [p["plan_name"] for p in response.json()]
    assert "Yoga" in names


def test_delete_plan(client):
    """
    DELETE /plans/{id} should remove the plan - a follow-up GET then 404s.
    """
    created = client.post("/plans", json={"plan_name": "Weight", "price": 1200, "duration_months": 1}).json()
    plan_id = created["plan_id"]

    delete_response = client.delete(f"/plans/{plan_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/plans/{plan_id}")
    assert get_response.status_code == 404
