from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.config.db import get_db
from app.schemas.horario_schema import (
    HorarioCreate,
    HorarioUpdate,
    HorarioResponse,
    BloqueoCreate
)
from app.services import horario_service
from app.security.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/horarios", tags=["Gestión de Horarios"])


@router.post(
    "/",
    response_model=HorarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Configurar horario disponible para un laboratorio"
)
def crear_horario(
    datos: HorarioCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("ADMINISTRADOR", "COORDINADOR"))
):
    return horario_service.crear_horario(db, datos)

@router.get(
    "/laboratorio/{laboratorio_id}",
    response_model=List[HorarioResponse],
    summary="Listar horarios de un laboratorio"
)
def listar_horarios(
    laboratorio_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    return horario_service.listar_horarios_laboratorio(db, laboratorio_id)


@router.get(
    "/{horario_id}",
    response_model=HorarioResponse,
    summary="Obtener un horario por ID"
)
def obtener_horario(
    horario_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    return horario_service.obtener_horario(db, horario_id)


@router.put(
    "/{horario_id}",
    response_model=HorarioResponse,
    summary="Actualizar un horario"
)
def actualizar_horario(
    horario_id: int,
    datos: HorarioUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("ADMINISTRADOR", "COORDINADOR"))
):
    return horario_service.actualizar_horario(db, horario_id, datos)


@router.patch(
    "/{horario_id}/bloquear",
    response_model=HorarioResponse,
    summary="Bloquear fecha especial"
)
def bloquear_fecha(
    horario_id: int,
    datos: BloqueoCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("ADMINISTRADOR", "COORDINADOR"))
):
    return horario_service.bloquear_fecha(db, horario_id, datos)


@router.patch(
    "/{horario_id}/disponible",
    response_model=HorarioResponse,
    summary="Desbloquear horario"
)
def desbloquear_horario(
    horario_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("ADMINISTRADOR", "COORDINADOR"))
):
    return horario_service.desbloquear_horario(db, horario_id)
