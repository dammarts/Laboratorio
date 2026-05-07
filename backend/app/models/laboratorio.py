from sqlalchemy import Column, Integer, String, Boolean
from app.config.db import Base

class Laboratorio(Base):
    __tablename__ = "laboratorios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    ubicacion = Column(String(255), nullable=False)
    capacidad_maxima = Column(Integer, nullable=False) # Ajustado el nombre
    recursos_disponibles = Column(String(500), nullable=True) # El campo que nos faltaba
    estado = Column(Boolean, default=True)