from pydantic import BaseModel, Field
from typing import Optional

# 1. El esquema base: Las propiedades comunes
class LaboratorioBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre del laboratorio")
    ubicacion: str = Field(..., min_length=3, max_length=150, description="Ubicación física (Ej: Bloque A - Piso 2)")
    capacidad_maxima: int = Field(..., gt=0, description="Capacidad máxima de estudiantes (debe ser mayor a 0)")
    recursos_disponibles: Optional[str] = Field(None, description="Equipos o recursos del laboratorio")
    estado: Optional[bool] = Field(True, description="Indica si el laboratorio está activo para reservas")

# 2.  El Esquema para crear
class LaboratorioCreate(LaboratorioBase):
    pass

# 3. El esquema para actualizar
class LaboratorioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    ubicacion: Optional[str] = Field(None, min_length=3, max_length=150)
    capacidad_maxima: Optional[int] = Field(None, gt=0)
    recursos_disponibles: Optional[str] = None
    estado: Optional[bool] = None

# 4. El esquema de respuesta
class LaboratorioResponse(LaboratorioBase):
    laboratorio_id: int

    class Config:
        from_attributes = True 