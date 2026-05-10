from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.db import get_db
from typing import List

from app.schemas.laboratorio_schema import LaboratorioCreate, LaboratorioUpdate, LaboratorioResponse
from app.services.laboratorio_service import LaboratorioService
from app.config.db import SessionLocal

router = APIRouter(prefix="/laboratorios", tags=["Gestión de Laboratorios"])
service = LaboratorioService()


@router.get("/", response_model=List[LaboratorioResponse])
def obtener_laboratorios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.obtener_todos(db, skip=skip, limit=limit)

@router.post("/", response_model=LaboratorioResponse, status_code=status.HTTP_201_CREATED)
def crear_laboratorio(laboratorio: LaboratorioCreate, db: Session = Depends(get_db)):
    return service.crear(db, laboratorio)

@router.get("/{id}", response_model=LaboratorioResponse)
def obtener_laboratorio(id: int, db: Session = Depends(get_db)):
    lab = service.obtener_por_id(db, id)
    if not lab:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    return lab

@router.put("/{id}", response_model=LaboratorioResponse)
def actualizar_laboratorio(id: int, laboratorio: LaboratorioUpdate, db: Session = Depends(get_db)):
    lab = service.actualizar(db, id, laboratorio)
    if not lab:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    return lab

@router.patch("/{id}/estado", response_model=LaboratorioResponse)
def desactivar_laboratorio(id: int, db: Session = Depends(get_db)):
    lab = service.desactivar(db, id)
    if not lab:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    return lab