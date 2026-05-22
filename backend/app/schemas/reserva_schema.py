import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.reserva import EstadoReserva


class ReservaCreate(BaseModel):
    laboratorio_id: int = Field(..., gt=0)
    curso: str = Field(..., min_length=1, max_length=150)
    fecha: datetime.date
    hora_inicio: datetime.time
    hora_fin: datetime.time
    num_estudiantes: Optional[int] = Field(None, ge=1, description="Número de estudiantes — no puede superar la capacidad del laboratorio")

    @field_validator("hora_fin")
    @classmethod
    def hora_fin_posterior(cls, hora_fin: datetime.time, info) -> datetime.time:
        hora_inicio = info.data.get("hora_inicio")
        if hora_inicio and hora_fin <= hora_inicio:
            raise ValueError("hora_fin debe ser posterior a hora_inicio")
        return hora_fin


class ReservaReprogramar(BaseModel):
    fecha: datetime.date
    hora_inicio: datetime.time
    hora_fin: datetime.time

    @field_validator("hora_fin")
    @classmethod
    def hora_fin_posterior(cls, hora_fin: datetime.time, info) -> datetime.time:
        hora_inicio = info.data.get("hora_inicio")
        if hora_inicio and hora_fin <= hora_inicio:
            raise ValueError("hora_fin debe ser posterior a hora_inicio")
        return hora_fin


class ReservaCancelar(BaseModel):
    motivo: str = Field(..., min_length=1, max_length=500)


class ReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reserva_id: int
    laboratorio_id: int
    usuario_creador_id: int
    curso: str
    fecha: datetime.date
    hora_inicio: datetime.time
    hora_fin: datetime.time
    estado: EstadoReserva
    motivo_cancelacion: Optional[str] = None
    fecha_creacion: datetime.datetime
    fecha_actualizacion: Optional[datetime.datetime] = None


class ReservaFiltros(BaseModel):
    laboratorio_id: Optional[int] = None
    usuario_creador_id: Optional[int] = None
    estado: Optional[EstadoReserva] = None
    fecha_desde: Optional[datetime.date] = None
    fecha_hasta: Optional[datetime.date] = None
