import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.security.dependencies import get_current_user, require_roles, UsuarioActual
from app.schemas.reserva_schema import (
    ReservaCreate, ReservaReprogramar, ReservaCancelar,
    ReservaResponse, ReservaFiltros,
)
from app.schemas.historial_reserva_schema import HistorialReservaResponse, HistorialFiltros
from app.models.reserva import EstadoReserva
import app.services.reserva_service as reserva_service
import app.repositories.historial_repository as historial_repo

router = APIRouter(prefix="/reservas", tags=["reservas"])


# IMPORTANTE: esta ruta debe ir ANTES de /{reserva_id} para que FastAPI
# no intente resolver "historial" como un entero en el path param.
@router.get(
    "/historial",
    response_model=List[HistorialReservaResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("ADMINISTRADOR", "ADMIN", "COORDINADOR"))],
)
def listar_historial(
    reserva_id: Optional[int] = Query(None),
    laboratorio_id: Optional[int] = Query(None),
    usuario_id: Optional[int] = Query(None),
    fecha_desde: Optional[datetime.date] = Query(None),
    fecha_hasta: Optional[datetime.date] = Query(None),
    db: Session = Depends(get_db),
):
    filtros = HistorialFiltros(
        reserva_id=reserva_id,
        laboratorio_id=laboratorio_id,
        usuario_id=usuario_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    return historial_repo.listar_historial(db, filtros)


@router.post(
    "/",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("ADMINISTRADOR", "ADMIN", "COORDINADOR", "DOCENTE"))],
)
def crear_reserva(
    data: ReservaCreate,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    return reserva_service.crear_reserva(db, data, usuario)


@router.get(
    "/",
    response_model=List[ReservaResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
def listar_reservas(
    laboratorio_id: Optional[int] = Query(None),
    usuario_creador_id: Optional[int] = Query(None),
    estado: Optional[EstadoReserva] = Query(None),
    fecha_desde: Optional[datetime.date] = Query(None),
    fecha_hasta: Optional[datetime.date] = Query(None),
    db: Session = Depends(get_db),
):
    filtros = ReservaFiltros(
        laboratorio_id=laboratorio_id,
        usuario_creador_id=usuario_creador_id,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    return reserva_service.listar_reservas(db, filtros)


@router.get(
    "/{reserva_id}",
    response_model=ReservaResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
def obtener_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
):
    return reserva_service.obtener_reserva(db, reserva_id)


@router.patch(
    "/{reserva_id}/cancelar",
    response_model=ReservaResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("ADMINISTRADOR", "ADMIN", "COORDINADOR", "DOCENTE"))],
)
def cancelar_reserva(
    reserva_id: int,
    data: ReservaCancelar,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    return reserva_service.cancelar_reserva(db, reserva_id, data, usuario)


@router.patch(
    "/{reserva_id}/reprogramar",
    response_model=ReservaResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("ADMINISTRADOR", "ADMIN", "COORDINADOR", "DOCENTE"))],
)
def reprogramar_reserva(
    reserva_id: int,
    data: ReservaReprogramar,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    return reserva_service.reprogramar_reserva(db, reserva_id, data, usuario)
