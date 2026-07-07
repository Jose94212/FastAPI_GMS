from fastapi import APIRouter

router_electronics = APIRouter()


@router_electronics.get('/electronics')
def list_electronics():
    """
    Fetches all electronic items
    :return:
    """
    return {'air-conditioners': 6, 'fan': 10, }
