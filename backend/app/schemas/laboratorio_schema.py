from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class LaboratorioBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150, description="Nombre del laboratorio")
    ubicacion: str = Field(..., min_length=3, max_length=200, description="Ubicación física (Ej: Bloque A - Piso 2)")
    capacidad_maxima: int = Field(..., gt=0, description="Capacidad máxima de estudiantes")
    tipo_laboratorio: str = Field(..., min_length=2, max_length=50, description="Tipo de laboratorio (Ej: Redes, Software)")
    recursos_disponibles: Optional[str] = Field(None, description="Equipos o recursos del laboratorio")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del laboratorio")
    estado: Optional[bool] = Field(True, description="Indica si el laboratorio está activo")


class LaboratorioCreate(LaboratorioBase):
    pass


class LaboratorioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=150)
    ubicacion: Optional[str] = Field(None, min_length=3, max_length=200)
    capacidad_maxima: Optional[int] = Field(None, gt=0)
    tipo_laboratorio: Optional[str] = Field(None, min_length=2, max_length=50)
    recursos_disponibles: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[bool] = None


class LaboratorioResponse(LaboratorioBase):
    model_config = ConfigDict(from_attributes=True)

    laboratorio_id: int
    created_at: datetime
