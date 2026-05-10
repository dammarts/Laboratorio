import enum
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class EstadoReserva(str, enum.Enum):
    ACTIVA       = "ACTIVA"
    CANCELADA    = "CANCELADA"
    REPROGRAMADA = "REPROGRAMADA"


class Reserva(Base):
    __tablename__ = "RESERVA"

    reserva_id          = Column(Integer, primary_key=True, index=True)
    laboratorio_id      = Column(Integer, ForeignKey("LABORATORIO.laboratorio_id"), nullable=False)
    usuario_creador_id  = Column(Integer, nullable=False)
    curso               = Column(String(150), nullable=False)
    fecha               = Column(Date, nullable=False)
    hora_inicio         = Column(Time, nullable=False)
    hora_fin            = Column(Time, nullable=False)
    estado              = Column(String(20), nullable=False, default=EstadoReserva.ACTIVA.value)
    motivo_cancelacion  = Column(String(500), nullable=True)
    fecha_creacion      = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=True)

    laboratorio = relationship("Laboratorio", back_populates="reservas")
    historial   = relationship("HistorialReserva", back_populates="reserva")
