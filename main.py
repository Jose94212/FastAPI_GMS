from fastapi import FastAPI
from routers import equipment, electronics, furniture, users

gms = FastAPI()

gms.include_router(equipment.router_equipment)
gms.include_router(electronics.router_electronics)
gms.include_router(furniture.router_furniture)
gms.include_router(users.router_users)


@gms.get("/")
def index() -> str:
    """
    Welcome message of the product
    :return: welcome message
    """
    return "Welcome to GainEthics!"
