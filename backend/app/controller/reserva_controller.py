from fastapi import APIRouter
from app.services.reserva_service import crear_reserva

router = APIRouter(prefix="/reservas")

@router.post("/")
def crear(data: dict):
    return crear_reserva(data)