import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.security.dependencies import require_roles
from app.schemas.reporte_schema import (
    FiltrosReporte,
    ReporteUsoLaboratorio,
    ReporteOcupacionMensual,
    ReporteDocente,
)
import app.services.reporte_service as reporte_service

router = APIRouter(prefix="/reportes", tags=["reportes"])

_CAMPOS_USO     = ["laboratorio_id", "nombre", "total_reservas", "horas_ocupadas", "reservas_canceladas"]
_CAMPOS_DOCENTE = ["usuario_id", "email", "total_reservas", "laboratorios_usados", "ultima_reserva"]


@router.get(
    "/uso-laboratorio",
    response_model=List[ReporteUsoLaboratorio],
    dependencies=[Depends(require_roles("ADMINISTRADOR", "ADMIN", "COORDINADOR"))],
)
def uso_laboratorio(
    laboratorio_id : Optional[int]           = Query(None),
    usuario_id     : Optional[int]           = Query(None),
    fecha_desde    : Optional[datetime.date] = Query(None),
    fecha_hasta    : Optional[datetime.date] = Query(None),
    db             : Session                 = Depends(get_db),
):
    filtros = FiltrosReporte(
        laboratorio_id=laboratorio_id,
        usuario_id=usuario_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    return reporte_service.generar_uso_laboratorio(db, filtros)


@router.get(
    "/uso-laboratorio/csv",
    response_class=StreamingResponse,
    dependencies=[Depends(require_roles("ADMINISTRADOR", "ADMIN", "COORDINADOR"))],
)
def uso_laboratorio_csv(
    laboratorio_id : Optional[int]           = Query(None),
    usuario_id     : Optional[int]           = Query(None),
    fecha_desde    : Optional[datetime.date] = Query(None),
    fecha_hasta    : Optional[datetime.date] = Query(None),
    db             : Session                 = Depends(get_db),
):
    filtros = FiltrosReporte(
        laboratorio_id=laboratorio_id,
        usuario_id=usuario_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    datos = reporte_service.generar_uso_laboratorio(db, filtros)
    return reporte_service.exportar_csv(datos, _CAMPOS_USO)


@router.get(
    "/ocupacion-mensual",
    response_model=List[ReporteOcupacionMensual],
    dependencies=[Depends(require_roles("ADMINISTRADOR", "ADMIN", "COORDINADOR"))],
)
def ocupacion_mensual(
    mes  : int     = Query(..., ge=1, le=12),
    anio : int     = Query(..., ge=2000),
    db   : Session = Depends(get_db),
):
    return reporte_service.generar_ocupacion_mensual(db, mes, anio)


@router.get(
    "/por-docente",
    response_model=List[ReporteDocente],
    dependencies=[Depends(require_roles("ADMINISTRADOR", "ADMIN", "COORDINADOR"))],
)
def por_docente(
    laboratorio_id : Optional[int]           = Query(None),
    usuario_id     : Optional[int]           = Query(None),
    fecha_desde    : Optional[datetime.date] = Query(None),
    fecha_hasta    : Optional[datetime.date] = Query(None),
    db             : Session                 = Depends(get_db),
):
    filtros = FiltrosReporte(
        laboratorio_id=laboratorio_id,
        usuario_id=usuario_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    return reporte_service.generar_por_docente(db, filtros)


@router.get(
    "/por-docente/csv",
    response_class=StreamingResponse,
    dependencies=[Depends(require_roles("ADMINISTRADOR", "ADMIN", "COORDINADOR"))],
)
def por_docente_csv(
    laboratorio_id : Optional[int]           = Query(None),
    usuario_id     : Optional[int]           = Query(None),
    fecha_desde    : Optional[datetime.date] = Query(None),
    fecha_hasta    : Optional[datetime.date] = Query(None),
    db             : Session                 = Depends(get_db),
):
    filtros = FiltrosReporte(
        laboratorio_id=laboratorio_id,
        usuario_id=usuario_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    datos = reporte_service.generar_por_docente(db, filtros)
    return reporte_service.exportar_csv(datos, _CAMPOS_DOCENTE)
