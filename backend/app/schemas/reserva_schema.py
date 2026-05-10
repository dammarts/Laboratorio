import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from app.models.reserva import EstadoReserva


class ReservaCreate(BaseModel):
    laboratorio_id : int            = Field(..., gt=0)
    curso          : str            = Field(..., min_length=1, max_length=150)
    fecha          : datetime.date
    hora_inicio    : datetime.time
    hora_fin       : datetime.time

    @validator("hora_fin")
    def hora_fin_posterior(cls, hora_fin: datetime.time, values: dict) -> datetime.time:
        hora_inicio = values.get("hora_inicio")
        if hora_inicio and hora_fin <= hora_inicio:
            raise ValueError("hora_fin debe ser posterior a hora_inicio")
        return hora_fin


class ReservaReprogramar(BaseModel):
    fecha       : datetime.date
    hora_inicio : datetime.time
    hora_fin    : datetime.time

    @validator("hora_fin")
    def hora_fin_posterior(cls, hora_fin: datetime.time, values: dict) -> datetime.time:
        hora_inicio = values.get("hora_inicio")
        if hora_inicio and hora_fin <= hora_inicio:
            raise ValueError("hora_fin debe ser posterior a hora_inicio")
        return hora_fin


class ReservaCancelar(BaseModel):
    motivo: str = Field(..., min_length=1, max_length=500)


class ReservaResponse(BaseModel):
    reserva_id          : int
    laboratorio_id      : int
    usuario_creador_id  : int
    curso               : str
    fecha               : datetime.date
    hora_inicio         : datetime.time
    hora_fin            : datetime.time
    estado              : EstadoReserva
    motivo_cancelacion  : Optional[str]
    fecha_creacion      : datetime.datetime
    fecha_actualizacion : Optional[datetime.datetime]

    class Config:
        from_attributes = True


class ReservaFiltros(BaseModel):
    laboratorio_id     : Optional[int]           = None
    usuario_creador_id : Optional[int]           = None
    estado             : Optional[EstadoReserva] = None
    fecha_desde        : Optional[datetime.date] = None
    fecha_hasta        : Optional[datetime.date] = None
