import datetime
from typing import Optional
from pydantic import BaseModel


class ReporteUsoLaboratorio(BaseModel):
    laboratorio_id      : int
    nombre              : str
    total_reservas      : int
    horas_ocupadas      : float
    reservas_canceladas : int

    class Config:
        from_attributes = True


class ReporteOcupacionMensual(BaseModel):
    mes                  : int
    anio                 : int
    laboratorio_id       : int
    nombre               : str
    total_reservas       : int
    porcentaje_ocupacion : float

    class Config:
        from_attributes = True


class ReporteDocente(BaseModel):
    usuario_id          : int
    email               : str
    total_reservas      : int
    laboratorios_usados : int
    ultima_reserva      : Optional[datetime.date]

    class Config:
        from_attributes = True


class FiltrosReporte(BaseModel):
    laboratorio_id : Optional[int]           = None
    usuario_id     : Optional[int]           = None
    mes            : Optional[int]           = None
    anio           : Optional[int]           = None
    fecha_desde    : Optional[datetime.date] = None
    fecha_hasta    : Optional[datetime.date] = None
