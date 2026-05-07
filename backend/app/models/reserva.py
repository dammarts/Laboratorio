from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class HorarioLaboratorio(Base):
    __tablename__ = "HORARIO_LABORATORIO"

    horario_id     = Column(Integer, primary_key=True, index=True)
    laboratorio_id = Column(Integer, ForeignKey("LABORATORIO.laboratorio_id"), nullable=False)
    dia_semana     = Column(Integer, nullable=False)
    hora_inicio    = Column(Time, nullable=False)
    hora_fin       = Column(Time, nullable=False)
    disponible     = Column(Boolean, default=True, nullable=False)
    fecha_bloqueo  = Column(Date, nullable=True)
    motivo_bloqueo = Column(String(300), nullable=True)

    laboratorio = relationship("Laboratorio", back_populates="horarios")


class RecursoLaboratorio(Base):
    __tablename__ = "RECURSO_LABORATORIO"

    recurso_id     = Column(Integer, primary_key=True, index=True)
    laboratorio_id = Column(Integer, ForeignKey("LABORATORIO.laboratorio_id"), nullable=False)
    nombre_recurso = Column(String(150), nullable=False)
    cantidad       = Column(Integer, default=0, nullable=False)
    descripcion    = Column(String(300), nullable=True)

    laboratorio = relationship("Laboratorio", back_populates="recursos")


class Reserva(Base):
    __tablename__ = "RESERVA"

    reserva_id         = Column(Integer, primary_key=True, index=True)
    usuario_id         = Column(Integer, nullable=False)
    laboratorio_id     = Column(Integer, ForeignKey("LABORATORIO.laboratorio_id"), nullable=False)
    nombre_curso       = Column(String(200), nullable=False)
    fecha_reserva      = Column(Date, nullable=False)
    hora_inicio        = Column(Time, nullable=False)
    hora_fin           = Column(Time, nullable=False)
    num_estudiantes    = Column(Integer, nullable=False)
    estado             = Column(String(20), default="PENDIENTE", nullable=False)
    motivo_cancelacion = Column(String(500), nullable=True)
    created_at         = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at         = Column(DateTime, nullable=True)

    laboratorio = relationship("Laboratorio", back_populates="reservas")
    auditorias  = relationship("AuditoriaReserva", back_populates="reserva")


class AuditoriaReserva(Base):
    __tablename__ = "AUDITORIA_RESERVA"

    auditoria_id = Column(Integer, primary_key=True, index=True)
    reserva_id   = Column(Integer, ForeignKey("RESERVA.reserva_id"), nullable=False)
    usuario_id   = Column(Integer, nullable=False)
    accion       = Column(String(30), nullable=False)
    detalle      = Column(String(500), nullable=True)
    fecha_accion = Column(DateTime, server_default=func.now(), nullable=False)
    ip_origen    = Column(String(45), nullable=True)

    reserva = relationship("Reserva")