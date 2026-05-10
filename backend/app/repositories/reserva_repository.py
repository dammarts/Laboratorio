import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.reserva import Reserva, EstadoReserva
from app.schemas.reserva_schema import ReservaFiltros


def guardar(db: Session, reserva: Reserva) -> Reserva:
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def obtener_por_id(db: Session, reserva_id: int) -> Optional[Reserva]:
    return db.query(Reserva).filter(Reserva.reserva_id == reserva_id).first()


def listar_con_filtros(db: Session, filtros: ReservaFiltros) -> List[Reserva]:
    query = db.query(Reserva)
    if filtros.laboratorio_id is not None:
        query = query.filter(Reserva.laboratorio_id == filtros.laboratorio_id)
    if filtros.usuario_creador_id is not None:
        query = query.filter(Reserva.usuario_creador_id == filtros.usuario_creador_id)
    if filtros.estado is not None:
        query = query.filter(Reserva.estado == filtros.estado.value)
    if filtros.fecha_desde is not None:
        query = query.filter(Reserva.fecha >= filtros.fecha_desde)
    if filtros.fecha_hasta is not None:
        query = query.filter(Reserva.fecha <= filtros.fecha_hasta)
    return query.all()


def existe_solapamiento(
    db: Session,
    laboratorio_id: int,
    fecha: datetime.date,
    hora_inicio: datetime.time,
    hora_fin: datetime.time,
    excluir_reserva_id: Optional[int] = None,
) -> bool:
    query = db.query(Reserva).filter(
        Reserva.laboratorio_id == laboratorio_id,
        Reserva.fecha == fecha,
        Reserva.estado != EstadoReserva.CANCELADA.value,
        Reserva.hora_inicio < hora_fin,
        Reserva.hora_fin > hora_inicio,
    )
    if excluir_reserva_id is not None:
        query = query.filter(Reserva.reserva_id != excluir_reserva_id)
    return query.first() is not None


def actualizar(db: Session, reserva: Reserva) -> Reserva:
    db.commit()
    db.refresh(reserva)
    return reserva
