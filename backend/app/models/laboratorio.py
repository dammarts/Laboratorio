from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Laboratorio(Base):
    __tablename__ = "LABORATORIO"

    laboratorio_id        = Column(Integer, primary_key=True, index=True)
    nombre                = Column(String(150), nullable=False)
    ubicacion             = Column(String(200), nullable=False)
    capacidad_maxima      = Column(Integer, nullable=False)
    tipo_laboratorio      = Column(String(50), nullable=False)
    recursos_disponibles  = Column(String(500), nullable=True)
    descripcion           = Column(String(500), nullable=True)
    estado                = Column(Boolean, default=True, nullable=False)
    created_at            = Column(DateTime, server_default=func.now(), nullable=False)

    horarios = relationship("HorarioLaboratorio", back_populates="laboratorio")
    recursos = relationship("RecursoLaboratorio", back_populates="laboratorio")
    reservas = relationship("Reserva", back_populates="laboratorio")