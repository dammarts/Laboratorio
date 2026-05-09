from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class HistorialReserva(Base):
    __tablename__ = "HISTORIAL_RESERVA"

    historial_id = Column(Integer, primary_key=True, index=True)
    reserva_id   = Column(Integer, ForeignKey("RESERVA.reserva_id"), nullable=False)
    usuario_id   = Column(Integer, nullable=False)
    accion       = Column(String(30), nullable=False)  # CREACION, CANCELACION, REPROGRAMACION
    detalle      = Column(String(500), nullable=True)
    fecha        = Column(DateTime, server_default=func.now(), nullable=False)

    reserva = relationship("Reserva", back_populates="historial")
