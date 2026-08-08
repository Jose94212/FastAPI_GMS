"""
Tests for the Electronics resource (gms_assets.electronics) - covers the
auth gate shared by electronics/furniture/equipment: every route needs a
logged-in member, delete needs the owner role specifically.
"""
from tests.integration.helpers import auth_headers


def test_create_without_login_is_rejected(client):
    """
    No Authorization header at all should 401 - get_current_user is a
    router-level dependency on every route here.
    """
    response = client.post("/electronics", json={"electro_name": "TV", "electro_count": 1})
    assert response.status_code == 401


def test_create_and_get_as_logged_in_member(client):
    """
    A plain (non-owner) member can create and fetch an electronics item.
    """
    headers = auth_headers(client, email="electro.member@example.com")

    create_response = client.post("/electronics", json={"electro_name": "TV", "electro_count": 1}, headers=headers)
    assert create_response.status_code == 201
    item = create_response.json()

    get_response = client.get(f"/electronics/{item['electro_id']}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["electro_name"] == "TV"


def test_get_not_found(client):
    """
    GET on a nonexistent electronics id should 404 (still needs a valid login).
    """
    headers = auth_headers(client, email="electro.404@example.com")
    response = client.get("/electronics/999", headers=headers)
    assert response.status_code == 404


def test_update_electronics(client):
    """
    PUT replaces the item's fields (full replacement, not partial).
    """
    headers = auth_headers(client, email="electro.update@example.com")
    item = client.post("/electronics", json={"electro_name": "TV", "electro_count": 1}, headers=headers).json()

    response = client.put(f"/electronics/{item['electro_id']}",
                          json={"electro_name": "TV - 65 inch", "electro_count": 2}, headers=headers)
    assert response.status_code == 200
    assert response.json()["electro_name"] == "TV - 65 inch"
    assert response.json()["electro_count"] == 2


def test_delete_as_plain_member_is_forbidden(client):
    """
    A logged-in member who is not the owner should get 403 on delete.
    """
    headers = auth_headers(client, email="electro.notowner@example.com")
    item = client.post("/electronics", json={"electro_name": "TV", "electro_count": 1}, headers=headers).json()

    response = client.delete(f"/electronics/{item['electro_id']}", headers=headers)
    assert response.status_code == 403


def test_delete_as_owner_succeeds(client):
    """
    The owner role can delete - a follow-up GET then 404s.
    """
    owner_headers = auth_headers(client, email="electro.owner@example.com", role="owner")
    item = client.post("/electronics", json={"electro_name": "TV", "electro_count": 1}, headers=owner_headers).json()

    delete_response = client.delete(f"/electronics/{item['electro_id']}", headers=owner_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/electronics/{item['electro_id']}", headers=owner_headers)
    assert get_response.status_code == 404
