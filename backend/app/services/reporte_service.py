import calendar
import csv
import io
from typing import List
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.schemas.reporte_schema import (
    FiltrosReporte,
    ReporteUsoLaboratorio,
    ReporteOcupacionMensual,
    ReporteDocente,
)
from app.repositories import reporte_repository

_HORAS_DISPONIBLES_DIA = 10.0  # referencia: 8am-6pm


def generar_uso_laboratorio(
    db: Session, filtros: FiltrosReporte
) -> List[ReporteUsoLaboratorio]:
    datos = reporte_repository.uso_por_laboratorio(db, filtros)
    return [ReporteUsoLaboratorio(**d) for d in datos]


def generar_ocupacion_mensual(
    db: Session, mes: int, anio: int
) -> List[ReporteOcupacionMensual]:
    datos = reporte_repository.ocupacion_mensual(db, mes, anio)
    dias_en_mes = calendar.monthrange(anio, mes)[1]
    horas_disponibles = dias_en_mes * _HORAS_DISPONIBLES_DIA
    for d in datos:
        d["porcentaje_ocupacion"] = round(
            (d["horas_ocupadas"] / horas_disponibles) * 100, 2
        )
    return [ReporteOcupacionMensual(**d) for d in datos]


def generar_por_docente(
    db: Session, filtros: FiltrosReporte
) -> List[ReporteDocente]:
    datos = reporte_repository.por_docente(db, filtros)
    return [ReporteDocente(**d) for d in datos]


def exportar_csv(datos: list, campos: list) -> StreamingResponse:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=campos, extrasaction="ignore")
    writer.writeheader()
    for item in datos:
        writer.writerow(
            item if isinstance(item, dict) else item.model_dump()
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=reporte.csv"},
    )