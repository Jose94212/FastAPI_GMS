from fastapi import FastAPI
from routers import equipments, electronics, furniture

gms = FastAPI()

gms.include_router(equipments.router_equipments)
gms.include_router(electronics.router_electronics)
gms.include_router(furniture.router_furniture)


@gms.get("/")
def index() -> str:
    """
    Welcome message of the product
    :return: welcome message
    """
    return "Welcome to GainEthics!"
