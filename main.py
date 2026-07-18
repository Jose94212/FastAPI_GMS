from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_db_and_tables
from gms_assets.electronics.router import router_electronics
from gms_assets.users.router import router_users
from gms_assets.furniture.router import router_furniture
from gms_assets.equipment.router import router_equipment


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
gms.include_router(router_users)


@gms.get("/")
def index() -> str:
    """
    Welcome message of the product
    :return: welcome message
    """
    return "Welcome to GainEthics!"
