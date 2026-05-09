import datetime
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.reserva import Reserva, EstadoReserva
from app.models.historial_reserva import HistorialReserva
from app.models.laboratorio import Laboratorio
from app.schemas.reserva_schema import ReservaCreate, ReservaReprogramar, ReservaCancelar, ReservaFiltros
from app.security.dependencies import UsuarioActual
import app.repositories.reserva_repository as reserva_repo
import app.repositories.historial_repository as historial_repo


def crear_reserva(db: Session, data: ReservaCreate, usuario: UsuarioActual) -> Reserva:
    laboratorio = db.query(Laboratorio).filter(Laboratorio.laboratorio_id == data.laboratorio_id).first()
    if not laboratorio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Laboratorio no encontrado")
    if not laboratorio.estado:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Laboratorio inactivo")
    if reserva_repo.existe_solapamiento(db, data.laboratorio_id, data.fecha, data.hora_inicio, data.hora_fin):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El horario solapa con una reserva existente")
    _validar_fecha_no_bloqueada(db, data.laboratorio_id, data.fecha)

    reserva = Reserva(
        laboratorio_id=data.laboratorio_id,
        usuario_creador_id=usuario.usuario_id,
        curso=data.curso,
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
    )
    reserva_repo.guardar(db, reserva)

    historial_repo.registrar_historial(db, HistorialReserva(
        reserva_id=reserva.reserva_id,
        usuario_id=usuario.usuario_id,
        accion="CREACION",
        detalle=f"Reserva creada para laboratorio {data.laboratorio_id} el {data.fecha}",
    ))

    return reserva


def listar_reservas(db: Session, filtros: ReservaFiltros) -> List[Reserva]:
    return reserva_repo.listar_con_filtros(db, filtros)


def obtener_reserva(db: Session, reserva_id: int) -> Reserva:
    reserva = reserva_repo.obtener_por_id(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    return reserva


def cancelar_reserva(db: Session, reserva_id: int, data: ReservaCancelar, usuario: UsuarioActual) -> Reserva:
    reserva = obtener_reserva(db, reserva_id)
    if reserva.estado == EstadoReserva.CANCELADA.value:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La reserva ya esta cancelada")

    reserva.estado = EstadoReserva.CANCELADA.value
    reserva.motivo_cancelacion = data.motivo
    reserva.fecha_actualizacion = datetime.datetime.now()
    reserva_repo.actualizar(db, reserva)

    historial_repo.registrar_historial(db, HistorialReserva(
        reserva_id=reserva.reserva_id,
        usuario_id=usuario.usuario_id,
        accion="CANCELACION",
        detalle=data.motivo,
    ))

    return reserva


def reprogramar_reserva(db: Session, reserva_id: int, data: ReservaReprogramar, usuario: UsuarioActual) -> Reserva:
    reserva = obtener_reserva(db, reserva_id)
    if reserva.estado == EstadoReserva.CANCELADA.value:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No se puede reprogramar una reserva cancelada")
    if reserva_repo.existe_solapamiento(db, reserva.laboratorio_id, data.fecha, data.hora_inicio, data.hora_fin, excluir_reserva_id=reserva_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El nuevo horario solapa con una reserva existente")

    reserva.fecha = data.fecha
    reserva.hora_inicio = data.hora_inicio
    reserva.hora_fin = data.hora_fin
    reserva.estado = EstadoReserva.REPROGRAMADA.value
    reserva.fecha_actualizacion = datetime.datetime.now()
    reserva_repo.actualizar(db, reserva)

    historial_repo.registrar_historial(db, HistorialReserva(
        reserva_id=reserva.reserva_id,
        usuario_id=usuario.usuario_id,
        accion="REPROGRAMACION",
        detalle=f"Reprogramada a {data.fecha} {data.hora_inicio}-{data.hora_fin}",
    ))

    return reserva


def _validar_fecha_no_bloqueada(db: Session, laboratorio_id: int, fecha: datetime.date) -> bool:
    # TODO: integrar con HorarioLaboratorio cuando Valeria entregue feature/gestion-horarios
    return True
