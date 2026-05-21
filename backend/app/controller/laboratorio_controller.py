from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.db import get_db
from app.schemas.laboratorio_schema import LaboratorioCreate, LaboratorioUpdate, LaboratorioResponse
from app.services.laboratorio_service import LaboratorioService

router = APIRouter(prefix="/laboratorios", tags=["Gestión de Laboratorios"])
service = LaboratorioService()

_LAB_NOT_FOUND = "Laboratorio no encontrado"
_404 = {404: {"description": _LAB_NOT_FOUND}}


@router.get("/", response_model=List[LaboratorioResponse])
def obtener_laboratorios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.obtener_todos(db, skip=skip, limit=limit)


@router.post("/", response_model=LaboratorioResponse, status_code=status.HTTP_201_CREATED)
def crear_laboratorio(laboratorio: LaboratorioCreate, db: Session = Depends(get_db)):
    return service.crear(db, laboratorio)


@router.get("/{id}", response_model=LaboratorioResponse, responses=_404)
def obtener_laboratorio(id: int, db: Session = Depends(get_db)):
    lab = service.obtener_por_id(db, id)
    if not lab:
        raise HTTPException(status_code=404, detail=_LAB_NOT_FOUND)
    return lab


@router.put("/{id}", response_model=LaboratorioResponse, responses=_404)
def actualizar_laboratorio(id: int, laboratorio: LaboratorioUpdate, db: Session = Depends(get_db)):
    lab = service.actualizar(db, id, laboratorio)
    if not lab:
        raise HTTPException(status_code=404, detail=_LAB_NOT_FOUND)
    return lab


@router.patch("/{id}/estado", response_model=LaboratorioResponse, responses=_404)
def desactivar_laboratorio(id: int, db: Session = Depends(get_db)):
    lab = service.desactivar(db, id)
    if not lab:
        raise HTTPException(status_code=404, detail=_LAB_NOT_FOUND)
    return lab
