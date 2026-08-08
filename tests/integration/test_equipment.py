"""
Tests for the Gym Equipment resource (gms_assets.equipment) - same auth-gated
CRUD pattern as Electronics/Furniture, plus the compute_values validator that
derives equip_cost_total/equip_next_maintenance_date when left blank.
"""
from tests.integration.helpers import auth_headers


def _equip_payload(**overrides):
    """
    A minimal valid GymEquipmentCreate body.
    """
    payload = {"equip_name": "Power Rack", "equip_count": 2, "equip_cost": 100}
    payload.update(overrides)
    return payload


def test_create_without_login_is_rejected(client):
    """
    No Authorization header should 401.
    """
    response = client.post("/gym_equipment", json=_equip_payload())
    assert response.status_code == 401


def test_create_computes_total_cost_when_not_given(client):
    """
    compute_values should fill equip_cost_total = count * cost when the
    caller doesn't provide one.
    """
    headers = auth_headers(client, email="equip.member@example.com")
    response = client.post("/gym_equipment", json=_equip_payload(), headers=headers)
    assert response.status_code == 201
    assert response.json()["equip_cost_total"] == 200


def test_create_respects_explicit_total_cost(client):
    """
    If the caller does provide equip_cost_total, compute_values should leave it alone.
    """
    headers = auth_headers(client, email="equip.explicit@example.com")
    response = client.post("/gym_equipment", json=_equip_payload(equip_cost_total=999), headers=headers)
    assert response.status_code == 201
    assert response.json()["equip_cost_total"] == 999


def test_get_not_found(client):
    """
    GET on a nonexistent equipment id should 404.
    """
    headers = auth_headers(client, email="equip.404@example.com")
    response = client.get("/gym_equipment/999", headers=headers)
    assert response.status_code == 404


def test_update_equipment(client):
    """
    PUT replaces the item's fields.
    """
    headers = auth_headers(client, email="equip.update@example.com")
    item = client.post("/gym_equipment", json=_equip_payload(), headers=headers).json()

    response = client.put(f"/gym_equipment/{item['equip_id']}",
                          json=_equip_payload(equip_name="Squat Rack", equip_count=5), headers=headers)
    assert response.status_code == 200
    assert response.json()["equip_name"] == "Squat Rack"
    assert response.json()["equip_count"] == 5


def test_delete_as_plain_member_is_forbidden(client):
    """
    A logged-in member who is not the owner should get 403 on delete.
    """
    headers = auth_headers(client, email="equip.notowner@example.com")
    item = client.post("/gym_equipment", json=_equip_payload(), headers=headers).json()

    response = client.delete(f"/gym_equipment/{item['equip_id']}", headers=headers)
    assert response.status_code == 403


def test_delete_as_owner_succeeds(client):
    """
    The owner role can delete - a follow-up GET then 404s.
    """
    owner_headers = auth_headers(client, email="equip.owner@example.com", role="owner")
    item = client.post("/gym_equipment", json=_equip_payload(), headers=owner_headers).json()

    delete_response = client.delete(f"/gym_equipment/{item['equip_id']}", headers=owner_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/gym_equipment/{item['equip_id']}", headers=owner_headers)
    assert get_response.status_code == 404
