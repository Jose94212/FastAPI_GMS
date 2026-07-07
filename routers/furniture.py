from fastapi import APIRouter

router_furniture = APIRouter()


@router_furniture.get('/furniture')
def list_free_weights():
    """
    thi method lists all free-weights available
    :return: sdf
    """
    return {'office desk': 1, 'sofa': 1, 'racks': 2, 'chairs': 5}
