from pydantic import BaseModel, field_validator, model_validator
from datetime import time, date
from typing import Optional



# Creacion de horarios
class HorarioCreate(BaseModel):
    laboratorio_id: int
    dia_semana: int          # 1=Lunes, 2=Martes ... 7=Domingo
    hora_inicio: time
    hora_fin: time

    @field_validator("dia_semana")
    @classmethod
    def validar_dia(cls, v):
        if v < 1 or v > 7:
            raise ValueError("dia_semana debe estar entre 1 (Lunes) y 7 (Domingo)")
        return v

    @model_validator(mode="after")
    def validar_horas(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValueError("hora_fin debe ser mayor que hora_inicio")
        return self



# Editar horario

class HorarioUpdate(BaseModel):
    dia_semana: Optional[int]  = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time]    = None
    disponible: Optional[bool]  = None

    @field_validator("dia_semana")
    @classmethod
    def validar_dia(cls, v):
        if v is not None and (v < 1 or v > 7):
            raise ValueError("dia_semana debe estar entre 1 y 7")
        return v



# Bloquear fecha especial

class BloqueoCreate(BaseModel):
    fecha_bloqueo: date
    motivo_bloqueo: str

    @field_validator("motivo_bloqueo")
    @classmethod
    def validar_motivo(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError("El motivo del bloqueo debe tener al menos 5 caracteres")
        return v.strip()

# respuesta del API

class HorarioResponse(BaseModel):
    horario_id:     int
    laboratorio_id: int
    dia_semana:     int
    hora_inicio:    time
    hora_fin:       time
    disponible:     bool
    fecha_bloqueo:  Optional[date] = None
    motivo_bloqueo: Optional[str]  = None

    # Propiedad calculada: nombre del día
    @property
    def nombre_dia(self) -> str:
        dias = {1:"Lunes", 2:"Martes", 3:"Miércoles",
                4:"Jueves", 5:"Viernes", 6:"Sábado", 7:"Domingo"}
        return dias.get(self.dia_semana, "Desconocido")

    model_config = {"from_attributes": True}
