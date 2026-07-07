from fastapi import APIRouter

router_equipments = APIRouter()


@router_equipments.get('/freeweights')
def list_free_weights():
    """
    thi method lists all free-weights available
    :return: sdf
    """
    return {'Dumbbells': 10, "Barbells": 12, "Weight Plates": 23, "Kettlebells": 242}
