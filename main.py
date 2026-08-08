from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_db_and_tables
from gms_assets.electronics.router import router_electronics
from gms_assets.furniture.router import router_furniture
from gms_assets.equipment.router import router_equipment
from gms_assets.locker.router import router_locker
from gms_assets.member_subscriptions.router import router_subscriptions
from gms_assets.members.router import router_member
from gms_assets.membership_plans.router import router_plans
from gms_assets.staff.router import router_staff


@asynccontextmanager
async def lifespan(app: FastAPI):
    """

    :param app:
    """
    create_db_and_tables()
    yield


gms = FastAPI(lifespan=lifespan)

gms.include_router(router_equipment)
gms.include_router(router_electronics)
gms.include_router(router_furniture)
gms.include_router(router_member)
gms.include_router(router_plans)
gms.include_router(router_subscriptions)
gms.include_router(router_staff)
gms.include_router(router_locker)


@gms.get("/")
def index() -> str:
    """
    Welcome message of the product
    :return: welcome message
    """
    return "Welcome to GainEthics!"
