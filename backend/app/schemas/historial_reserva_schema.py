import datetime
from typing import Optional
from pydantic import BaseModel


class HistorialReservaResponse(BaseModel):
    historial_id : int
    reserva_id   : int
    usuario_id   : int
    accion       : str
    detalle      : Optional[str]
    fecha        : datetime.datetime

    class Config:
        from_attributes = True


class HistorialFiltros(BaseModel):
    reserva_id     : Optional[int]           = None
    laboratorio_id : Optional[int]           = None
    usuario_id     : Optional[int]           = None
    fecha_desde    : Optional[datetime.date] = None
    fecha_hasta    : Optional[datetime.date] = None
