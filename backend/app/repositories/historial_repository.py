from typing import List
from sqlalchemy.orm import Session
from app.models.historial_reserva import HistorialReserva
from app.models.reserva import Reserva
from app.schemas.historial_reserva_schema import HistorialFiltros


def registrar_historial(db: Session, historial: HistorialReserva) -> HistorialReserva:
    db.add(historial)
    db.commit()
    db.refresh(historial)
    return historial


def listar_historial(db: Session, filtros: HistorialFiltros) -> List[HistorialReserva]:
    query = db.query(HistorialReserva)
    if filtros.reserva_id is not None:
        query = query.filter(HistorialReserva.reserva_id == filtros.reserva_id)
    if filtros.usuario_id is not None:
        query = query.filter(HistorialReserva.usuario_id == filtros.usuario_id)
    if filtros.laboratorio_id is not None:
        query = query.join(Reserva).filter(Reserva.laboratorio_id == filtros.laboratorio_id)
    if filtros.fecha_desde is not None:
        query = query.filter(HistorialReserva.fecha >= filtros.fecha_desde)
    if filtros.fecha_hasta is not None:
        query = query.filter(HistorialReserva.fecha <= filtros.fecha_hasta)
    return query.all()
