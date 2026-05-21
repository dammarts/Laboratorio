import pytest
from unittest.mock import MagicMock, patch
from app.services.laboratorio_service import LaboratorioService
from app.schemas.laboratorio_schema import LaboratorioCreate, LaboratorioUpdate
from app.models.laboratorio import Laboratorio


# FIXTURES

@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def service():
    return LaboratorioService()


@pytest.fixture
def laboratorio_activo():
    lab = MagicMock(spec=Laboratorio)
    lab.id = 1
    lab.nombre = "Lab Informática 101"
    lab.ubicacion = "Bloque A - Piso 1"
    lab.capacidad_maxima = 30
    lab.recursos_disponibles = "30 computadores"
    lab.estado = True
    return lab


@pytest.fixture
def laboratorio_activo():
    lab = MagicMock(spec=Laboratorio)
    lab.laboratorio_id = 1
    lab.id = 1
    lab.nombre = "Lab Informática 101"
    lab.ubicacion = "Bloque A - Piso 1"
    lab.capacidad_maxima = 30
    lab.recursos_disponibles = "30 computadores"
    lab.estado = True
    return lab



# validación obtener información

class TestObtenerTodos:

    def test_obtener_todos_retorna_lista(self, db, service, laboratorio_activo):
        """Retorna lista de laboratorios."""
        db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [laboratorio_activo]
        resultado = service.obtener_todos(db)
        assert resultado == [laboratorio_activo]

    def test_obtener_todos_lista_vacia(self, db, service):
        """Retorna lista vacía si no hay laboratorios."""
        db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = service.obtener_todos(db)
        assert resultado == []

    def test_obtener_todos_con_paginacion(self, db, service, laboratorio_activo):
        """Aplica skip y limit correctamente."""
        db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [laboratorio_activo]
        resultado = service.obtener_todos(db, skip=0, limit=10)
        assert resultado == [laboratorio_activo]



# Validación obtener información mediante el ID


class TestObtenerPorId:

    def test_obtener_por_id_existente(self, db, service, laboratorio_activo):
        """ Retorna laboratorio cuando existe."""
        db.query.return_value.filter.return_value.first.return_value = laboratorio_activo
        resultado = service.obtener_por_id(db, 1)
        assert resultado.id == 1
        assert resultado.nombre == "Lab Informática 101"

    def test_obtener_por_id_inexistente(self, db, service):
        """ Retorna None cuando no existe."""
        db.query.return_value.filter.return_value.first.return_value = None
        resultado = service.obtener_por_id(db, 999)
        assert resultado is None


# Validacion crear laboratorio

class TestCrearLaboratorio:

    def test_crear_laboratorio_exitoso(self, db, service, laboratorio_activo):
        """ Crea un laboratorio correctamente."""
        datos = LaboratorioCreate(
            nombre="Lab Informática 101",
            ubicacion="Bloque A - Piso 1",
            capacidad_maxima=30,
            tipo_laboratorio="INFORMATICA",
            recursos_disponibles="30 computadores",
            estado=True
        )

        db.add.return_value = None
        db.commit.return_value = None
        db.refresh.return_value = None

        with patch("app.repositories.laboratorio_repository.Laboratorio",
                   return_value=laboratorio_activo):
            resultado = service.crear(db, datos)
            assert db.add.called
            assert db.commit.called

    def test_crear_laboratorio_sin_recursos(self, db, service):
        """ Crea laboratorio sin recursos_disponibles."""
        datos = LaboratorioCreate(
            nombre="Lab Química 301",
            ubicacion="Bloque C - Piso 3",
            capacidad_maxima=24,
            tipo_laboratorio="QUIMICA",
            estado=True
        )

        lab = MagicMock()
        lab.nombre = "Lab Química 301"
        lab.recursos_disponibles = None

        db.add.return_value = None
        db.commit.return_value = None
        db.refresh.return_value = None

        with patch("app.repositories.laboratorio_repository.Laboratorio", return_value=lab):
            resultado = service.crear(db, datos)
            assert db.commit.called


# Validación actualizar laboratorio


class TestActualizarLaboratorio:

    def test_actualizar_nombre_exitoso(self, db, service, laboratorio_activo):
        """ Actualiza el nombre correctamente."""
        datos = LaboratorioUpdate(nombre="Lab Informática Actualizado")
        db.query.return_value.filter.return_value.first.return_value = laboratorio_activo
        db.commit.return_value = None
        db.refresh.return_value = None

        resultado = service.actualizar(db, 1, datos)
        assert resultado is not None

    def test_actualizar_laboratorio_inexistente(self, db, service):
        """ Retorna None si laboratorio no existe."""
        datos = LaboratorioUpdate(nombre="Nuevo nombre")
        db.query.return_value.filter.return_value.first.return_value = None

        resultado = service.actualizar(db, 999, datos)
        assert resultado is None

    def test_actualizar_capacidad(self, db, service, laboratorio_activo):
        """ Actualiza capacidad máxima correctamente."""
        datos = LaboratorioUpdate(capacidad_maxima=50)
        db.query.return_value.filter.return_value.first.return_value = laboratorio_activo
        db.commit.return_value = None
        db.refresh.return_value = None

        resultado = service.actualizar(db, 1, datos)
        assert resultado is not None


# Validar desactivar laboriatorio


class TestDesactivarLaboratorio:

    def test_desactivar_exitoso(self, db, service, laboratorio_activo):
        """ Desactiva laboratorio correctamente."""
        db.query.return_value.filter.return_value.first.return_value = laboratorio_activo
        db.commit.return_value = None
        db.refresh.return_value = None

        resultado = service.desactivar(db, 1)
        assert resultado is not None
        assert db.commit.called

    def test_desactivar_inexistente(self, db, service):
        """ Retorna None si laboratorio no existe."""
        db.query.return_value.filter.return_value.first.return_value = None
        resultado = service.desactivar(db, 999)
        assert resultado is None



#  validaciones del schema


class TestLaboratorioSchema:

    def test_nombre_muy_corto(self):
        """ Lanza error si nombre tiene menos de 3 caracteres."""
        with pytest.raises(Exception):
            LaboratorioCreate(
                nombre="AB",
                ubicacion="Bloque A",
                capacidad_maxima=10
            )

    def test_capacidad_cero(self):
        """Lanza error si capacidad es 0."""
        with pytest.raises(Exception):
            LaboratorioCreate(
                nombre="Lab Test",
                ubicacion="Bloque A",
                capacidad_maxima=0
            )

    def test_capacidad_negativa(self):
        """ Lanza error si capacidad es negativa."""
        with pytest.raises(Exception):
            LaboratorioCreate(
                nombre="Lab Test",
                ubicacion="Bloque A",
                capacidad_maxima=-5
            )

    def test_schema_valido(self):
        """Crea schema correctamente con datos válidos."""
        lab = LaboratorioCreate(
            nombre="Lab Informática",
            ubicacion="Bloque A - Piso 1",
            capacidad_maxima=30,
            tipo_laboratorio="INFORMATICA"
        )
        assert lab.nombre == "Lab Informática"
        assert lab.capacidad_maxima == 30
        assert lab.estado == True

    def test_ubicacion_muy_corta(self):
        """ Lanza error si ubicacion tiene menos de 3 caracteres."""
        with pytest.raises(Exception):
            LaboratorioCreate(
                nombre="Lab Test",
                ubicacion="AB",
                capacidad_maxima=10
            )