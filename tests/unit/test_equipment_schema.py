"""
Unit tests for GymEquipmentCreate's compute_values validator
(gms_assets.equipment.schemas) - derives equip_cost_total and
equip_next_maintenance_date when the caller leaves them blank.
No client, no DB, no HTTP.
"""
from datetime import datetime, timedelta

from gms_assets.equipment.schemas import GymEquipmentCreate


def test_cost_total_defaults_to_count_times_cost():
    equipment = GymEquipmentCreate(equip_name="Rack", equip_count=3, equip_cost=100)
    assert equipment.equip_cost_total == 300


def test_cost_total_is_left_alone_when_given_explicitly():
    equipment = GymEquipmentCreate(equip_name="Rack", equip_count=3, equip_cost=100, equip_cost_total=999)
    assert equipment.equip_cost_total == 999


def test_next_maintenance_date_defaults_to_one_year_after_purchase():
    purchase_date = datetime(2026, 1, 1)
    equipment = GymEquipmentCreate(equip_name="Rack", equip_count=1, equip_cost=100,
                                   equip_purchase_date=purchase_date)
    assert equipment.equip_next_maintenance_date == purchase_date + timedelta(days=365)


def test_next_maintenance_date_is_left_alone_when_given_explicitly():
    purchase_date = datetime(2026, 1, 1)
    custom_maintenance_date = datetime(2026, 6, 1)
    equipment = GymEquipmentCreate(equip_name="Rack", equip_count=1, equip_cost=100,
                                   equip_purchase_date=purchase_date,
                                   equip_next_maintenance_date=custom_maintenance_date)
    assert equipment.equip_next_maintenance_date == custom_maintenance_date
