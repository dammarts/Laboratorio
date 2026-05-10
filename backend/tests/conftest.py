import os
os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.config.db import get_db
from app.models.base import Base
from app.models import laboratorio, reserva, historial_reserva  # registrar modelos en Base
from app.models.laboratorio import Laboratorio

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def db(create_tables):
    session = TestingSessionLocal()
    yield session
    session.rollback()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def laboratorio_activo(db):
    lab = Laboratorio(
        nombre="Lab Computo A",
        ubicacion="Edificio Principal Piso 1",
        capacidad_maxima=30,
        tipo_laboratorio="COMPUTO",
        estado=True,
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab


@pytest.fixture()
def laboratorio_inactivo(db):
    lab = Laboratorio(
        nombre="Lab Inactivo B",
        ubicacion="Edificio Sur Piso 2",
        capacidad_maxima=20,
        tipo_laboratorio="ELECTRONICA",
        estado=False,
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab
