from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct

from app.models.reserva import Reserva, EstadoReserva
from app.models.laboratorio import Laboratorio
from app.models.usuario import Usuario
from app.schemas.reporte_schema import FiltrosReporte


def uso_por_laboratorio(db: Session, filtros: FiltrosReporte) -> List[dict]:
    query = (
        db.query(
            Laboratorio.laboratorio_id,
            Laboratorio.nombre,
            func.count(Reserva.reserva_id).label("total_reservas"),
            (func.coalesce(
                func.sum(
                    case(
                        (
                            Reserva.estado != EstadoReserva.CANCELADA.value,
                            # PostgreSQL utiliza extract('epoch') para calcular diferencias de tiempo
                            func.extract('epoch', Reserva.hora_fin - Reserva.hora_inicio) / 60.0
                        ),
                        else_=0
                    )
                ), 0
            ) / 60.0).label("horas_ocupadas"),
            func.sum(
                case(
                    (Reserva.estado == EstadoReserva.CANCELADA.value, 1),
                    else_=0
                )
            ).label("reservas_canceladas"),
        )
        .join(Reserva, Reserva.laboratorio_id == Laboratorio.laboratorio_id)
        .group_by(Laboratorio.laboratorio_id, Laboratorio.nombre)
    )

    if filtros.laboratorio_id is not None:
        query = query.filter(
            Laboratorio.laboratorio_id == filtros.laboratorio_id
        )

    if filtros.usuario_id is not None:
        query = query.filter(
            Reserva.usuario_creador_id == filtros.usuario_id
        )

    if filtros.fecha_desde is not None:
        query = query.filter(
            Reserva.fecha >= filtros.fecha_desde
        )

    if filtros.fecha_hasta is not None:
        query = query.filter(
            Reserva.fecha <= filtros.fecha_hasta
        )

    return [dict(row._mapping) for row in query.all()]


def ocupacion_mensual(db: Session, mes: int, anio: int) -> List[dict]:
    rows = (
        db.query(
            Laboratorio.laboratorio_id,
            Laboratorio.nombre,
            func.count(Reserva.reserva_id).label("total_reservas"),
            (func.coalesce(
                func.sum(
                    func.extract('epoch', Reserva.hora_fin - Reserva.hora_inicio) / 60.0
                ),
                0
            ) / 60.0).label("horas_ocupadas"),
        )
        .join(Reserva, Reserva.laboratorio_id == Laboratorio.laboratorio_id)
        .filter(
            func.extract('month', Reserva.fecha) == mes,
            func.extract('year', Reserva.fecha) == anio,
            Reserva.estado != EstadoReserva.CANCELADA.value,
        )
        .group_by(
            Laboratorio.laboratorio_id,
            Laboratorio.nombre
        )
        .all()
    )

    resultado = []
    for row in rows:
        d = dict(row._mapping)
        d["mes"] = mes
        d["anio"] = anio
        resultado.append(d)

    return resultado


def por_docente(db: Session, filtros: FiltrosReporte) -> List[dict]:
    query = (
        db.query(
            Usuario.usuario_id,
            Usuario.email,
            func.count(
                case(
                    (
                        Reserva.estado != EstadoReserva.CANCELADA.value,
                        Reserva.reserva_id
                    ),
                    else_=None
                )
            ).label("total_reservas"),
            func.count(
                distinct(Reserva.laboratorio_id)
            ).label("laboratorios_usados"),
            func.max(Reserva.fecha).label("ultima_reserva"),
        )
        .join(
            Reserva,
            Reserva.usuario_creador_id == Usuario.usuario_id
        )
        .filter(Usuario.rol == "DOCENTE")
        .group_by(
            Usuario.usuario_id,
            Usuario.email
        )
    )

    if filtros.usuario_id is not None:
        query = query.filter(
            Usuario.usuario_id == filtros.usuario_id
        )

    if filtros.laboratorio_id is not None:
        query = query.filter(
            Reserva.laboratorio_id == filtros.laboratorio_id
        )

    if filtros.fecha_desde is not None:
        query = query.filter(
            Reserva.fecha >= filtros.fecha_desde
        )

    if filtros.fecha_hasta is not None:
        query = query.filter(
            Reserva.fecha <= filtros.fecha_hasta
        )

    return [dict(row._mapping) for row in query.all()]
