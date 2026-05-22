import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class HistorialReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    historial_id: int
    reserva_id: int
    usuario_id: int
    accion: str
    detalle: Optional[str] = None
    fecha: datetime.datetime


class HistorialFiltros(BaseModel):
    reserva_id: Optional[int] = None
    laboratorio_id: Optional[int] = None
    usuario_id: Optional[int] = None
    fecha_desde: Optional[datetime.date] = None
    fecha_hasta: Optional[datetime.date] = None
