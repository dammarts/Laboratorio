from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from typing import Optional

from app.models.horario import HorarioLaboratorio


def crear_horario(db: Session, datos: dict) -> HorarioLaboratorio:
    """Inserta un nuevo horario en la BD."""
    horario = HorarioLaboratorio(**datos)
    db.add(horario)
    db.commit()
    db.refresh(horario)
    return horario


def obtener_por_id(db: Session, horario_id: int) -> Optional[HorarioLaboratorio]:
    """Busca un horario por su ID."""
    return db.query(HorarioLaboratorio).filter(
        HorarioLaboratorio.horario_id == horario_id
    ).first()


def listar_por_laboratorio(db: Session, laboratorio_id: int) -> list[HorarioLaboratorio]:
    """Retorna todos los horarios de un laboratorio, ordenados por día y hora."""
    return db.query(HorarioLaboratorio).filter(
        HorarioLaboratorio.laboratorio_id == laboratorio_id
    ).order_by(
        HorarioLaboratorio.dia_semana,
        HorarioLaboratorio.hora_inicio
    ).all()


def existe_horario_mismo_dia(
    db: Session,
    laboratorio_id: int,
    dia_semana: int,
    excluir_id: Optional[int] = None
) -> bool:
    """
    Verifica si ya existe un horario para ese laboratorio en ese día.
    Se usa para evitar duplicados al crear o actualizar.
    """
    query = db.query(HorarioLaboratorio).filter(
        and_(
            HorarioLaboratorio.laboratorio_id == laboratorio_id,
            HorarioLaboratorio.dia_semana == dia_semana
        )
    )
    if excluir_id:
        query = query.filter(HorarioLaboratorio.horario_id != excluir_id)
    return query.first() is not None


def actualizar_horario(
    db: Session,
    horario: HorarioLaboratorio,
    datos: dict
) -> HorarioLaboratorio:
    """Actualiza los campos enviados en datos (solo los que no sean None)."""
    for campo, valor in datos.items():
        if valor is not None:
            setattr(horario, campo, valor)
    db.commit()
    db.refresh(horario)
    return horario


def bloquear_fecha(
    db: Session,
    horario: HorarioLaboratorio,
    fecha: date,
    motivo: str
) -> HorarioLaboratorio:
    """Bloquea un horario en una fecha especial (mantenimiento, festivo, etc.)."""
    horario.disponible     = False
    horario.fecha_bloqueo  = fecha
    horario.motivo_bloqueo = motivo
    db.commit()
    db.refresh(horario)
    return horario


def desbloquear_horario(
    db: Session,
    horario: HorarioLaboratorio
) -> HorarioLaboratorio:
    """Vuelve a poner un horario como disponible y limpia el bloqueo."""
    horario.disponible     = True
    horario.fecha_bloqueo  = None
    horario.motivo_bloqueo = None
    db.commit()
    db.refresh(horario)
    return horario