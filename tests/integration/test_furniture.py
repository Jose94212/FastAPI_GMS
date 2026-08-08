"""
Tests for the Furniture resource (gms_assets.furniture) - same auth-gated
CRUD pattern as Electronics/Equipment.
"""
from tests.integration.helpers import auth_headers


def test_create_without_login_is_rejected(client):
    """
    No Authorization header should 401.
    """
    response = client.post("/furniture", json={"fur_name": "Chair", "fur_count": 1, "fur_cost": 50})
    assert response.status_code == 401


def test_create_and_list_as_logged_in_member(client):
    """
    A plain member can create furniture and see it in the list.
    """
    headers = auth_headers(client, email="fur.member@example.com")

    create_response = client.post("/furniture", json={"fur_name": "Chair", "fur_count": 1, "fur_cost": 50}, headers=headers)
    assert create_response.status_code == 201

    list_response = client.get("/furniture", headers=headers)
    assert list_response.status_code == 200
    names = [f["fur_name"] for f in list_response.json()]
    assert "Chair" in names


def test_get_not_found(client):
    """
    GET on a nonexistent furniture id should 404.
    """
    headers = auth_headers(client, email="fur.404@example.com")
    response = client.get("/furniture/999", headers=headers)
    assert response.status_code == 404


def test_update_furniture(client):
    """
    PUT replaces the item's fields.
    """
    headers = auth_headers(client, email="fur.update@example.com")
    item = client.post("/furniture", json={"fur_name": "Chair", "fur_count": 1, "fur_cost": 50}, headers=headers).json()

    response = client.put(f"/furniture/{item['fur_id']}",
                          json={"fur_name": "Bench", "fur_count": 3, "fur_cost": 50}, headers=headers)
    assert response.status_code == 200
    assert response.json()["fur_name"] == "Bench"
    assert response.json()["fur_count"] == 3


def test_delete_as_plain_member_is_forbidden(client):
    """
    A logged-in member who is not the owner should get 403 on delete.
    """
    headers = auth_headers(client, email="fur.notowner@example.com")
    item = client.post("/furniture", json={"fur_name": "Chair", "fur_count": 1, "fur_cost": 50}, headers=headers).json()

    response = client.delete(f"/furniture/{item['fur_id']}", headers=headers)
    assert response.status_code == 403


def test_delete_as_owner_succeeds(client):
    """
    The owner role can delete - a follow-up GET then 404s.
    """
    owner_headers = auth_headers(client, email="fur.owner@example.com", role="owner")
    item = client.post("/furniture", json={"fur_name": "Chair", "fur_count": 1, "fur_cost": 50}, headers=owner_headers).json()

    delete_response = client.delete(f"/furniture/{item['fur_id']}", headers=owner_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/furniture/{item['fur_id']}", headers=owner_headers)
    assert get_response.status_code == 404
