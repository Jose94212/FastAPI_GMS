"""
One-off script to populate gms.db with realistic sample data across every resource.
Run once from the project root:  python3 seed_data.py

Inserts directly via the DB session (bypassing the API layer), in dependency order:
  1. Electronics, Furniture, Equipment (no dependencies)
  2. Membership Plans (no dependencies)
  3. Members (no dependencies)
  4. Staff (depends on Members existing, via member_id FK)
  5. Subscriptions (depends on Members + Plans existing, via member_id/plan_id FK)
"""
from datetime import date, timedelta

from sqlmodel import Session

from database import engine, create_db_and_tables

from gms_assets.electronics.models import GymElectronicsDB
from gms_assets.furniture.models import FurnitureDB
from gms_assets.equipment.models import GymEquipmentDB
from gms_assets.membership_plans.models import GymMembershipPlansDB
from gms_assets.membership_plans.schemas import PlanNames
from gms_assets.members.models import GymMembersDB, GymStaffsDB
from gms_assets.members.schemas import Gender, MemberStatus, GymRoles
from gms_assets.member_subscriptions.model import GymSubscriptionsDB
from gms_assets.member_subscriptions.schemas import SubscriptionStatus


def seed():
    create_db_and_tables()

    with Session(engine) as db_session:
        # --- 1. Electronics ---
        electronics = [
            GymElectronicsDB(electro_name='Wall-Mounted TV - 55"', electro_description="Cardio zone display", electro_count=4),
            GymElectronicsDB(electro_name="Sound System - Ceiling Speakers", electro_description="Studio audio", electro_count=8),
            GymElectronicsDB(electro_name="Heart Rate Monitor Kiosk", electro_description=None, electro_count=2),
            GymElectronicsDB(electro_name="Check-in Tablet - Front Desk", electro_description="Reception check-in", electro_count=1),
        ]
        db_session.add_all(electronics)

        # --- 2. Furniture ---
        furniture = [
            FurnitureDB(fur_name="Weight Bench (Flat/Incline)", fur_description=None, fur_count=10, fur_cost=150),
            FurnitureDB(fur_name="Locker Unit - 20 Compartment", fur_description="Changing room", fur_count=3, fur_cost=600),
            FurnitureDB(fur_name="Reception Desk", fur_description=None, fur_count=1, fur_cost=800),
            FurnitureDB(fur_name="Waiting Area Sofa", fur_description="3-seater", fur_count=2, fur_cost=400),
        ]
        db_session.add_all(furniture)

        # --- 3. Equipment ---
        # GymEquipmentCreate computes equip_cost_total/equip_next_maintenance_date itself via a
        # model_validator, so build via the Create schema first, then hand off to the DB model.
        from gms_assets.equipment.schemas import GymEquipmentCreate

        equipment_data = [
            dict(equip_name="Olympic Barbell Set", equip_count=6, equip_lease=False, equip_cost=250),
            dict(equip_name="Adjustable Dumbbells (5-50 lb)", equip_count=12, equip_lease=False, equip_cost=180),
            dict(equip_name="Power Rack", equip_description="Squat/bench rack", equip_count=3, equip_lease=False, equip_cost=900),
            dict(equip_name="Treadmill - Commercial Grade", equip_count=8, equip_lease=True, equip_cost=2200),
            dict(equip_name="Rowing Machine", equip_count=4, equip_lease=True, equip_cost=1100),
            dict(equip_name="Kettlebell Set (10-40 lb)", equip_count=5, equip_lease=False, equip_cost=150),
        ]
        equipment = [GymEquipmentDB.model_validate(GymEquipmentCreate(**data)) for data in equipment_data]
        db_session.add_all(equipment)

        # --- 4. Membership Plans ---
        plans = [
            GymMembershipPlansDB(plan_name=PlanNames.cardio, price=1000, duration_months=1),
            GymMembershipPlansDB(plan_name=PlanNames.weight, price=1200, duration_months=1),
            GymMembershipPlansDB(plan_name=PlanNames.weight_cardio, price=2000, duration_months=3),
            GymMembershipPlansDB(plan_name=PlanNames.yoga, price=1000, duration_months=1),
        ]
        db_session.add_all(plans)
        db_session.commit()
        for p in plans:
            db_session.refresh(p)

        # --- 5. Members (mix of plain members and staff roles) ---
        members_data = [
            # (f_name, l_name, email, phone, dob, gender, role)
            ("Alex", "Morgan", "alex.morgan@ironpeak.gym", "9000000001", date(1985, 3, 12), Gender.male, GymRoles.owner),
            ("Sam", "Rivera", "sam.rivera@ironpeak.gym", "9000000002", date(1990, 7, 22), Gender.male, GymRoles.trainer),
            ("Jordan", "Lee", "jordan.lee@ironpeak.gym", "9000000003", date(1992, 11, 5), Gender.others, GymRoles.trainer),
            ("Taylor", "Brooks", "taylor.brooks@ironpeak.gym", "9000000004", date(1995, 2, 18), Gender.female, GymRoles.receptionist),
            ("Casey", "Kim", "casey.kim@ironpeak.gym", "9000000005", date(1988, 9, 30), Gender.female, GymRoles.dietitian),
            ("Morgan", "Ellis", "morgan.ellis@gmail.com", "9000000006", date(1998, 5, 14), Gender.male, GymRoles.member),
            ("Riley", "Chen", "riley.chen@gmail.com", "9000000007", date(2000, 1, 9), Gender.female, GymRoles.member),
            ("Jamie", "Patel", "jamie.patel@gmail.com", "9000000008", date(1996, 6, 25), Gender.others, GymRoles.member),
            ("Drew", "Anderson", "drew.anderson@gmail.com", "9000000009", date(1993, 12, 1), Gender.male, GymRoles.member),
            ("Avery", "Thompson", "avery.thompson@gmail.com", "9000000010", date(1999, 4, 8), Gender.female, GymRoles.member),
        ]

        members = []
        for f_name, l_name, email, phone, dob, gender, role in members_data:
            m = GymMembersDB(
                f_name=f_name, l_name=l_name, email=email, phone=phone, dob=dob, gender=gender,
                emergency_contact_name="Emergency Contact", emergency_contact_number="9111111111",
                blood_group="O+", role=role, member_status=MemberStatus.active,
            )
            members.append(m)
        db_session.add_all(members)
        db_session.commit()
        for m in members:
            db_session.refresh(m)

        # --- 6. Staff rows for every member whose role isn't plain "member" ---
        staff_salaries = {
            GymRoles.owner: 80000,
            GymRoles.trainer: 35000,
            GymRoles.receptionist: 22000,
            GymRoles.dietitian: 40000,
        }
        staff_rows = []
        for m in members:
            if m.role != GymRoles.member:
                staff_rows.append(GymStaffsDB(
                    member_id=m.member_id,
                    salary=staff_salaries[m.role],
                    hire_date=m.joining_date,
                ))
        db_session.add_all(staff_rows)

        # --- 7. Subscriptions for the plain-member subset, across different plans/statuses ---
        plain_members = [m for m in members if m.role == GymRoles.member]
        subscriptions = [
            GymSubscriptionsDB(member_id=plain_members[0].member_id, plan_id=plans[0].plan_id,
                               start_date=date.today() - timedelta(days=10), end_date=date.today() + timedelta(days=20),
                               status=SubscriptionStatus.active),
            GymSubscriptionsDB(member_id=plain_members[1].member_id, plan_id=plans[1].plan_id,
                               start_date=date.today() - timedelta(days=40), end_date=date.today() + timedelta(days=50),
                               status=SubscriptionStatus.active),
            GymSubscriptionsDB(member_id=plain_members[2].member_id, plan_id=plans[2].plan_id,
                               start_date=date.today() - timedelta(days=100), end_date=date.today() + timedelta(days=170),
                               status=SubscriptionStatus.active),
            GymSubscriptionsDB(member_id=plain_members[3].member_id, plan_id=plans[3].plan_id,
                               start_date=date.today() - timedelta(days=200), end_date=date.today() - timedelta(days=170),
                               status=SubscriptionStatus.expired),
            GymSubscriptionsDB(member_id=plain_members[4].member_id, plan_id=plans[0].plan_id,
                               start_date=date.today() - timedelta(days=5), end_date=date.today() - timedelta(days=2),
                               status=SubscriptionStatus.cancelled),
        ]
        db_session.add_all(subscriptions)

        db_session.commit()

    print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed()
