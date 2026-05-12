from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Usuario(Base):
    __tablename__ = "USUARIO"

    usuario_id    = Column(Integer, primary_key=True, index=True)
    email         = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    rol           = Column(String(20), nullable=False)
    activo        = Column(Boolean, default=True, nullable=False)
    created_at    = Column(DateTime, server_default=func.now(), nullable=False)

    reservas = relationship("Reserva", back_populates="usuario")
