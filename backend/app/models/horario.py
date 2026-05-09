from sqlalchemy import Column, Integer, String, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
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
