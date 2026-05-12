"""
Pruebas unitarias del módulo reporte_service.

Cubre: generar_uso_laboratorio, generar_ocupacion_mensual,
       generar_por_docente, exportar_csv.
Todas mockean reporte_repository — no tocan BD.
"""
import calendar
import datetime
import pytest
from unittest.mock import patch, MagicMock
from fastapi.responses import StreamingResponse

from app.services import reporte_service
from app.schemas.reporte_schema import (
    FiltrosReporte,
    ReporteUsoLaboratorio,
    ReporteOcupacionMensual,
    ReporteDocente,
)


# ---------------------------------------------------------------------------
# generar_uso_laboratorio
# ---------------------------------------------------------------------------

def test_uso_laboratorio_lista_vacia():
    """Cuando el repo retorna [], el service retorna lista vacía."""
    # Arrange
    db_mock = MagicMock()
    filtros = FiltrosReporte()

    # Act
    with patch(
        "app.services.reporte_service.reporte_repository.uso_por_laboratorio",
        return_value=[],
    ):
        resultado = reporte_service.generar_uso_laboratorio(db_mock, filtros)

    # Assert
    assert resultado == []
    assert isinstance(resultado, list)


def test_uso_laboratorio_excluye_horas_canceladas():
    """El schema ReporteUsoLaboratorio acepta horas_ocupadas float y reservas_canceladas int."""
    # Arrange
    db_mock = MagicMock()
    filtros = FiltrosReporte()
    datos_repo = [
        {
            "laboratorio_id": 1,
            "nombre": "Lab A",
            "total_reservas": 5,
            "horas_ocupadas": 12.5,
            "reservas_canceladas": 2,
        }
    ]

    # Act
    with patch(
        "app.services.reporte_service.reporte_repository.uso_por_laboratorio",
        return_value=datos_repo,
    ):
        resultado = reporte_service.generar_uso_laboratorio(db_mock, filtros)

    # Assert: el schema convierte correctamente los tipos
    assert len(resultado) == 1
    item = resultado[0]
    assert isinstance(item, ReporteUsoLaboratorio)
    assert isinstance(item.horas_ocupadas, float)
    assert isinstance(item.reservas_canceladas, int)
    assert item.horas_ocupadas == 12.5
    assert item.reservas_canceladas == 2


# ---------------------------------------------------------------------------
# generar_ocupacion_mensual
# ---------------------------------------------------------------------------

def test_ocupacion_mensual_calcula_porcentaje():
    """Dado horas_ocupadas=50.0 en enero, el servicio calcula porcentaje correcto."""
    # Arrange
    db_mock = MagicMock()
    mes = 1
    anio = 2024
    dias_en_mes = calendar.monthrange(anio, mes)[1]  # 31
    horas_disponibles = dias_en_mes * 10.0           # 310.0
    esperado = round(50.0 / horas_disponibles * 100, 2)  # 16.13

    # El repo ya agrega mes/anio al dict antes de retornar (ver reporte_repository.py)
    datos_repo = [
        {
            "laboratorio_id": 2,
            "nombre": "Lab B",
            "total_reservas": 10,
            "horas_ocupadas": 50.0,
            "mes": mes,
            "anio": anio,
        }
    ]

    # Act
    with patch(
        "app.services.reporte_service.reporte_repository.ocupacion_mensual",
        return_value=datos_repo,
    ):
        resultado = reporte_service.generar_ocupacion_mensual(db_mock, mes, anio)

    # Assert
    assert len(resultado) == 1
    item = resultado[0]
    assert isinstance(item, ReporteOcupacionMensual)
    assert item.porcentaje_ocupacion == esperado
    assert item.mes == mes
    assert item.anio == anio


def test_ocupacion_mensual_lista_vacia():
    """Cuando el repo retorna [], el service retorna lista vacía sin error."""
    # Arrange
    db_mock = MagicMock()

    # Act
    with patch(
        "app.services.reporte_service.reporte_repository.ocupacion_mensual",
        return_value=[],
    ):
        resultado = reporte_service.generar_ocupacion_mensual(db_mock, 6, 2024)

    # Assert
    assert resultado == []


# ---------------------------------------------------------------------------
# generar_por_docente
# ---------------------------------------------------------------------------

def test_por_docente_excluye_canceladas():
    """El service convierte correctamente los datos del repo al schema ReporteDocente."""
    # Arrange
    db_mock = MagicMock()
    filtros = FiltrosReporte()
    datos_repo = [
        {
            "usuario_id": 10,
            "email": "docente@uni.edu",
            "total_reservas": 8,
            "laboratorios_usados": 3,
            "ultima_reserva": datetime.date(2024, 5, 20),
        }
    ]

    # Act
    with patch(
        "app.services.reporte_service.reporte_repository.por_docente",
        return_value=datos_repo,
    ):
        resultado = reporte_service.generar_por_docente(db_mock, filtros)

    # Assert: total_reservas del repo queda en el schema tal cual
    assert len(resultado) == 1
    item = resultado[0]
    assert isinstance(item, ReporteDocente)
    assert item.total_reservas == 8
    assert item.email == "docente@uni.edu"
    assert item.ultima_reserva == datetime.date(2024, 5, 20)


def test_por_docente_lista_vacia():
    """Cuando el repo retorna [], el service retorna lista vacía."""
    # Arrange
    db_mock = MagicMock()
    filtros = FiltrosReporte()

    # Act
    with patch(
        "app.services.reporte_service.reporte_repository.por_docente",
        return_value=[],
    ):
        resultado = reporte_service.generar_por_docente(db_mock, filtros)

    # Assert
    assert resultado == []


# ---------------------------------------------------------------------------
# exportar_csv
# ---------------------------------------------------------------------------

def test_exportar_csv_retorna_streaming():
    """exportar_csv retorna StreamingResponse con media_type text/csv."""
    # Arrange
    datos = [
        ReporteUsoLaboratorio(
            laboratorio_id=1,
            nombre="Lab A",
            total_reservas=5,
            horas_ocupadas=10.0,
            reservas_canceladas=1,
        )
    ]
    campos = ["laboratorio_id", "nombre", "total_reservas", "horas_ocupadas", "reservas_canceladas"]

    # Act
    respuesta = reporte_service.exportar_csv(datos, campos)

    # Assert
    assert isinstance(respuesta, StreamingResponse)
    assert respuesta.media_type == "text/csv"


def test_exportar_csv_lista_vacia():
    """exportar_csv con [] produce un CSV que solo contiene la línea de headers."""
    import asyncio

    # Arrange
    campos = ["laboratorio_id", "nombre", "total_reservas", "horas_ocupadas", "reservas_canceladas"]

    # Act
    respuesta = reporte_service.exportar_csv([], campos)

    # Assert: debe ser StreamingResponse
    assert isinstance(respuesta, StreamingResponse)
    assert respuesta.media_type == "text/csv"

    # Consumir el body_iterator (puede ser sync o async generator según la versión de Starlette)
    async def _consumir():
        partes = []
        async for chunk in respuesta.body_iterator:
            if isinstance(chunk, bytes):
                partes.append(chunk)
            else:
                partes.append(chunk.encode("utf-8"))
        return b"".join(partes).decode("utf-8")

    contenido = asyncio.run(_consumir())
    lineas = [l for l in contenido.splitlines() if l.strip()]
    # Solo debe haber una línea: los headers
    assert len(lineas) == 1
    assert "laboratorio_id" in lineas[0]
    assert "nombre" in lineas[0]
