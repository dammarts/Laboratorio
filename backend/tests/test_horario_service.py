import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import time, date

from app.services.horario_service import (
    crear_horario,
    listar_horarios_laboratorio,
    obtener_horario,
    actualizar_horario,
    bloquear_fecha,
    desbloquear_horario
)
from app.schemas.horario_schema import HorarioCreate, BloqueoCreate
from app.models.reserva import HorarioLaboratorio
from app.models.laboratorio import Laboratorio


#Se pueden utilizar en las siguientes pruebas

@pytest.fixture
def db():
    """Simula la sesión de base de datos."""
    return MagicMock()


@pytest.fixture
def laboratorio_activo():
    """Laboratorio de prueba activo."""
    lab = MagicMock(spec=Laboratorio)
    lab.laboratorio_id = 1
    lab.nombre = "Lab Informática 101"
    lab.estado = True
    return lab


@pytest.fixture
def laboratorio_inactivo():
    """Laboratorio de prueba inactivo."""
    lab = MagicMock(spec=Laboratorio)
    lab.laboratorio_id = 2
    lab.nombre = "Lab Cerrado"
    lab.estado = False
    return lab


@pytest.fixture
def horario_disponible():
    """Horario de prueba disponible."""
    h = MagicMock(spec=HorarioLaboratorio)
    h.horario_id = 1
    h.laboratorio_id = 1
    h.dia_semana = 1
    h.hora_inicio = time(7, 0)
    h.hora_fin = time(10, 0)
    h.disponible = True
    h.fecha_bloqueo = None
    h.motivo_bloqueo = None
    return h


@pytest.fixture
def horario_bloqueado():
    """Horario de prueba bloqueado."""
    h = MagicMock(spec=HorarioLaboratorio)
    h.horario_id = 2
    h.laboratorio_id = 1
    h.dia_semana = 2
    h.hora_inicio = time(8, 0)
    h.hora_fin = time(12, 0)
    h.disponible = False
    h.fecha_bloqueo = date(2026, 12, 25)
    h.motivo_bloqueo = "Festivo navidad"
    return h


# Validacion creacion de horario


class TestCrearHorario:

    def test_crear_horario_exitoso(self, db, laboratorio_activo, horario_disponible):
        """ Caso positivo: crea un horario correctamente."""
        datos = HorarioCreate(
            laboratorio_id=1,
            dia_semana=1,
            hora_inicio=time(7, 0),
            hora_fin=time(10, 0)
        )

        with patch("app.services.horario_service._obtener_laboratorio_activo", return_value=laboratorio_activo), \
             patch("app.services.horario_service.horario_repo.existe_horario_mismo_dia", return_value=False), \
             patch("app.services.horario_service.horario_repo.crear_horario", return_value=horario_disponible):

            resultado = crear_horario(db, datos)
            assert resultado.horario_id == 1
            assert resultado.disponible is True

    def test_crear_horario_laboratorio_inexistente(self, db):
        """ Caso negativo: laboratorio no existe."""
        datos = HorarioCreate(
            laboratorio_id=999,
            dia_semana=1,
            hora_inicio=time(7, 0),
            hora_fin=time(10, 0)
        )

        with patch("app.services.horario_service._obtener_laboratorio_activo",
                   side_effect=HTTPException(status_code=404, detail="No existe")):
            with pytest.raises(HTTPException) as exc:
                crear_horario(db, datos)
            assert exc.value.status_code == 404

    def test_crear_horario_laboratorio_inactivo(self, db):
        """ Caso negativo: laboratorio inactivo."""
        datos = HorarioCreate(
            laboratorio_id=2,
            dia_semana=1,
            hora_inicio=time(7, 0),
            hora_fin=time(10, 0)
        )

        with patch("app.services.horario_service._obtener_laboratorio_activo",
                   side_effect=HTTPException(status_code=400, detail="Inactivo")):
            with pytest.raises(HTTPException) as exc:
                crear_horario(db, datos)
            assert exc.value.status_code == 400

    def test_crear_horario_duplicado(self, db, laboratorio_activo):
        """ Caso negativo: ya existe horario ese día."""
        datos = HorarioCreate(
            laboratorio_id=1,
            dia_semana=1,
            hora_inicio=time(7, 0),
            hora_fin=time(10, 0)
        )

        with patch("app.services.horario_service._obtener_laboratorio_activo", return_value=laboratorio_activo), \
             patch("app.services.horario_service.horario_repo.existe_horario_mismo_dia", return_value=True):
            with pytest.raises(HTTPException) as exc:
                crear_horario(db, datos)
            assert exc.value.status_code == 409


# Validación bloqueo de fechas


class TestBloquearFecha:

    def test_bloquear_fecha_exitoso(self, db, horario_disponible):
        """ Caso positivo: bloquea una fecha correctamente."""
        datos = BloqueoCreate(
            fecha_bloqueo=date(2026, 12, 25),
            motivo_bloqueo="Festivo navidad"
        )

        horario_bloqueado = MagicMock()
        horario_bloqueado.disponible = False

        with patch("app.services.horario_service._obtener_horario_o_404", return_value=horario_disponible), \
             patch("app.services.horario_service.horario_repo.bloquear_fecha", return_value=horario_bloqueado):

            resultado = bloquear_fecha(db, 1, datos)
            assert resultado.disponible is False

    def test_bloquear_fecha_ya_bloqueada(self, db, horario_bloqueado):
        """ Caso negativo: fecha ya está bloqueada."""
        datos = BloqueoCreate(
            fecha_bloqueo=date(2026, 12, 25),
            motivo_bloqueo="Festivo navidad"
        )

        with patch("app.services.horario_service._obtener_horario_o_404", return_value=horario_bloqueado):
            with pytest.raises(HTTPException) as exc:
                bloquear_fecha(db, 2, datos)
            assert exc.value.status_code == 409

    def test_bloquear_fecha_horario_inexistente(self, db):
        """ Caso negativo: horario no existe."""
        datos = BloqueoCreate(
            fecha_bloqueo=date(2026, 12, 25),
            motivo_bloqueo="Festivo"
        )

        with patch("app.services.horario_service._obtener_horario_o_404",
                   side_effect=HTTPException(status_code=404, detail="No encontrado")):
            with pytest.raises(HTTPException) as exc:
                bloquear_fecha(db, 999, datos)
            assert exc.value.status_code == 404



# Validación desbloqueo de horarios

class TestDesbloquearHorario:

    def test_desbloquear_exitoso(self, db, horario_bloqueado):
        """ Caso positivo: desbloquea un horario correctamente."""
        horario_desbloqueado = MagicMock()
        horario_desbloqueado.disponible = True

        with patch("app.services.horario_service._obtener_horario_o_404", return_value=horario_bloqueado), \
             patch("app.services.horario_service.horario_repo.desbloquear_horario", return_value=horario_desbloqueado):

            resultado = desbloquear_horario(db, 2)
            assert resultado.disponible is True

    def test_desbloquear_horario_ya_disponible(self, db, horario_disponible):
        """ Caso negativo: horario ya está disponible."""
        with patch("app.services.horario_service._obtener_horario_o_404", return_value=horario_disponible):
            with pytest.raises(HTTPException) as exc:
                desbloquear_horario(db, 1)
            assert exc.value.status_code == 400


# Validar listar horarios


class TestListarHorarios:

    def test_listar_horarios_exitoso(self, db, laboratorio_activo, horario_disponible):
        """ Caso positivo: lista horarios de un laboratorio."""
        with patch("app.services.horario_service._obtener_laboratorio_activo", return_value=laboratorio_activo), \
             patch("app.services.horario_service.horario_repo.listar_por_laboratorio",
                   return_value=[horario_disponible]):

            resultado = listar_horarios_laboratorio(db, 1)
            assert len(resultado) == 1

    def test_listar_horarios_laboratorio_inexistente(self, db):
        """ Caso negativo: laboratorio no existe."""
        with patch("app.services.horario_service._obtener_laboratorio_activo",
                   side_effect=HTTPException(status_code=404, detail="No existe")):
            with pytest.raises(HTTPException) as exc:
                listar_horarios_laboratorio(db, 999)
            assert exc.value.status_code == 404

# Validacion horario repository

class TestHorarioRepository:

    def test_obtener_por_id_existente(self, db, horario_disponible):
        """ Retorna horario cuando existe."""
        db.query.return_value.filter.return_value.first.return_value = horario_disponible

        from app.repositories.horario_repository import obtener_por_id
        resultado = obtener_por_id(db, 1)
        assert resultado.horario_id == 1

    def test_obtener_por_id_inexistente(self, db):
        """ Retorna None cuando no existe."""
        db.query.return_value.filter.return_value.first.return_value = None

        from app.repositories.horario_repository import obtener_por_id
        resultado = obtener_por_id(db, 999)
        assert resultado is None

    def test_existe_horario_mismo_dia_true(self, db, horario_disponible):
        """ Retorna True cuando ya existe horario ese día."""
        db.query.return_value.filter.return_value.first.return_value = horario_disponible

        from app.repositories.horario_repository import existe_horario_mismo_dia
        resultado = existe_horario_mismo_dia(db, 1, 1)
        assert resultado is True

    def test_existe_horario_mismo_dia_false(self, db):
        """ Retorna False cuando no existe horario ese día."""
        db.query.return_value.filter.return_value.first.return_value = None

        from app.repositories.horario_repository import existe_horario_mismo_dia
        resultado = existe_horario_mismo_dia(db, 1, 1)
        assert resultado is False

    def test_listar_por_laboratorio(self, db, horario_disponible):
        """ Retorna lista de horarios de un laboratorio."""
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [horario_disponible]

        from app.repositories.horario_repository import listar_por_laboratorio
        resultado = listar_por_laboratorio(db, 1)
        assert len(resultado) == 1

    def test_desbloquear_horario(self, db, horario_bloqueado):
        """ Desbloquea un horario correctamente."""
        horario_bloqueado.disponible = False
        db.commit.return_value = None
        db.refresh.return_value = None

        from app.repositories.horario_repository import desbloquear_horario
        resultado = desbloquear_horario(db, horario_bloqueado)
        assert horario_bloqueado.disponible is True
        assert horario_bloqueado.fecha_bloqueo is None
        assert horario_bloqueado.motivo_bloqueo is None


# Validación: obtener horario y actualizar horario


class TestObtenerYActualizarHorario:

    def test_obtener_horario_exitoso(self, db, horario_disponible):
        """ Retorna horario existente."""
        with patch("app.services.horario_service._obtener_horario_o_404", return_value=horario_disponible):
            resultado = obtener_horario(db, 1)
            assert resultado.horario_id == 1

    def test_obtener_horario_inexistente(self, db):
        """ Lanza 404 si no existe."""
        with patch("app.services.horario_service._obtener_horario_o_404",
                   side_effect=HTTPException(status_code=404, detail="No encontrado")):
            with pytest.raises(HTTPException) as exc:
                obtener_horario(db, 999)
            assert exc.value.status_code == 404

    def test_actualizar_horario_exitoso(self, db, horario_disponible):
        """ Actualiza horario correctamente."""
        from app.schemas.horario_schema import HorarioUpdate
        datos = HorarioUpdate(dia_semana=2)
        horario_actualizado = MagicMock()
        horario_actualizado.dia_semana = 2

        with patch("app.services.horario_service._obtener_horario_o_404", return_value=horario_disponible), \
             patch("app.services.horario_service.horario_repo.existe_horario_mismo_dia", return_value=False), \
             patch("app.services.horario_service.horario_repo.actualizar_horario", return_value=horario_actualizado):
            resultado = actualizar_horario(db, 1, datos)
            assert resultado.dia_semana == 2

    def test_actualizar_horario_dia_duplicado(self, db, horario_disponible):
        """ Lanza 409 si el nuevo día ya tiene horario."""
        from app.schemas.horario_schema import HorarioUpdate
        datos = HorarioUpdate(dia_semana=3)

        with patch("app.services.horario_service._obtener_horario_o_404", return_value=horario_disponible), \
             patch("app.services.horario_service.horario_repo.existe_horario_mismo_dia", return_value=True):
            with pytest.raises(HTTPException) as exc:
                actualizar_horario(db, 1, datos)
            assert exc.value.status_code == 409



#validaciones del schema

class TestHorarioSchema:

    def test_hora_fin_menor_hora_inicio(self):
        """ Lanza error si hora_fin <= hora_inicio."""
        with pytest.raises(Exception):
            HorarioCreate(
                laboratorio_id=1,
                dia_semana=1,
                hora_inicio=time(10, 0),
                hora_fin=time(7, 0)
            )

    def test_dia_semana_invalido(self):
        """ Lanza error si dia_semana está fuera de rango."""
        with pytest.raises(Exception):
            HorarioCreate(
                laboratorio_id=1,
                dia_semana=8,
                hora_inicio=time(7, 0),
                hora_fin=time(10, 0)
            )

    def test_dia_semana_valido(self):
        """ Crea schema correctamente con datos válidos."""
        h = HorarioCreate(
            laboratorio_id=1,
            dia_semana=5,
            hora_inicio=time(8, 0),
            hora_fin=time(12, 0)
        )
        assert h.dia_semana == 5

    def test_motivo_bloqueo_muy_corto(self):
        """ Lanza error si motivo tiene menos de 5 caracteres."""
        with pytest.raises(Exception):
            BloqueoCreate(
                fecha_bloqueo=date(2026, 12, 25),
                motivo_bloqueo="abc"
            )
# Validación repository crear y bloquear


class TestHorarioRepositoryAvanzado:

    def test_crear_horario_repository(self, db, horario_disponible):
        """ Crea horario en BD correctamente."""
        db.add.return_value = None
        db.commit.return_value = None
        db.refresh.return_value = None

        datos = {
            "laboratorio_id": 1,
            "dia_semana": 1,
            "hora_inicio": time(7, 0),
            "hora_fin": time(10, 0),
            "disponible": True,
            "fecha_bloqueo": None,
            "motivo_bloqueo": None
        }

        from app.repositories.horario_repository import crear_horario
        from app.models.reserva import HorarioLaboratorio

        with patch("app.repositories.horario_repository.HorarioLaboratorio", return_value=horario_disponible):
            resultado = crear_horario(db, datos)
            assert db.add.called
            assert db.commit.called

    def test_bloquear_fecha_repository(self, db, horario_disponible):
        """ Bloquea fecha en BD correctamente."""
        db.commit.return_value = None
        db.refresh.return_value = None

        from app.repositories.horario_repository import bloquear_fecha
        resultado = bloquear_fecha(db, horario_disponible, date(2026, 12, 25), "Festivo")

        assert horario_disponible.disponible is False
        assert horario_disponible.fecha_bloqueo == date(2026, 12, 25)
        assert horario_disponible.motivo_bloqueo == "Festivo"

    def test_actualizar_horario_repository(self, db, horario_disponible):
        """ Actualiza campos del horario correctamente."""
        db.commit.return_value = None
        db.refresh.return_value = None

        from app.repositories.horario_repository import actualizar_horario
        datos = {"dia_semana": 3}
        actualizar_horario(db, horario_disponible, datos)

        assert horario_disponible.dia_semana == 3
        assert db.commit.called

    def test_existe_horario_con_exclusion(self, db, horario_disponible):
        """ Excluye ID al verificar duplicado en actualización."""
        db.query.return_value.filter.return_value.filter.return_value.first.return_value = None

        from app.repositories.horario_repository import existe_horario_mismo_dia
        resultado = existe_horario_mismo_dia(db, 1, 1, excluir_id=1)
        assert resultado is False

    def test_listar_horarios_vacio(self, db):
        """ Retorna lista vacía si no hay horarios."""
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        from app.repositories.horario_repository import listar_por_laboratorio
        resultado = listar_por_laboratorio(db, 99)
        assert resultado == []