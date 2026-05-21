import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ReporteUsoLaboratorio(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    laboratorio_id: int
    nombre: str
    total_reservas: int
    horas_ocupadas: float
    reservas_canceladas: int


class ReporteOcupacionMensual(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mes: int
    anio: int
    laboratorio_id: int
    nombre: str
    total_reservas: int
    porcentaje_ocupacion: float


class ReporteDocente(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    email: str
    total_reservas: int
    laboratorios_usados: int
    ultima_reserva: Optional[datetime.date]


class FiltrosReporte(BaseModel):
    laboratorio_id: Optional[int] = None
    usuario_id: Optional[int] = None
    mes: Optional[int] = None
    anio: Optional[int] = None
    fecha_desde: Optional[datetime.date] = None
    fecha_hasta: Optional[datetime.date] = None
