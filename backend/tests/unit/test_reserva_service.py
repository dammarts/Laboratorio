import datetime
import pytest
from fastapi import HTTPException

from app.services import reserva_service
from app.repositories import reserva_repository
from app.schemas.reserva_schema import ReservaCreate, ReservaCancelar, ReservaReprogramar
from app.security.dependencies import UsuarioActual
from app.models.reserva import Reserva, EstadoReserva

USUARIO_DOCENTE = UsuarioActual(usuario_id=1, email="docente@test.com", rol="DOCENTE")


# ============================================================
# SOLAPAMIENTO — algoritmo directo sobre el repository
# ============================================================

class TestExisteSolapamiento:
    """Reserva base fija: laboratorio_activo, 2026-06-15, 10:00-12:00."""

    FECHA = datetime.date(2026, 6, 15)

    @pytest.fixture(autouse=True)
    def reserva_base(self, db, laboratorio_activo):
        r = Reserva(
            laboratorio_id=laboratorio_activo.laboratorio_id,
            usuario_creador_id=1,
            curso="Curso Base",
            fecha=self.FECHA,
            hora_inicio=datetime.time(10, 0),
            hora_fin=datetime.time(12, 0),
            estado=EstadoReserva.ACTIVA.value,
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        self.lab_id = laboratorio_activo.laboratorio_id
        self.reserva_id = r.reserva_id

    def test_solapamiento_exacto(self, db):
        assert reserva_repository.existe_solapamiento(
            db, self.lab_id, self.FECHA,
            datetime.time(10, 0), datetime.time(12, 0),
        ) is True

    def test_solapamiento_parcial_inicio(self, db):
        # nueva: 09:00-11:00
        assert reserva_repository.existe_solapamiento(
            db, self.lab_id, self.FECHA,
            datetime.time(9, 0), datetime.time(11, 0),
        ) is True

    def test_solapamiento_parcial_fin(self, db):
        # nueva: 11:00-13:00
        assert reserva_repository.existe_solapamiento(
            db, self.lab_id, self.FECHA,
            datetime.time(11, 0), datetime.time(13, 0),
        ) is True

    def test_nueva_contenida_en_existente(self, db):
        # nueva: 10:30-11:30
        assert reserva_repository.existe_solapamiento(
            db, self.lab_id, self.FECHA,
            datetime.time(10, 30), datetime.time(11, 30),
        ) is True

    def test_existente_contenida_en_nueva(self, db):
        # nueva: 09:00-13:00
        assert reserva_repository.existe_solapamiento(
            db, self.lab_id, self.FECHA,
            datetime.time(9, 0), datetime.time(13, 0),
        ) is True

    def test_sin_solapamiento_contiguo(self, db):
        # nueva: 12:00-14:00 (contiguo, sin solapamiento)
        assert reserva_repository.existe_solapamiento(
            db, self.lab_id, self.FECHA,
            datetime.time(12, 0), datetime.time(14, 0),
        ) is False

    def test_excluir_propia_reserva_no_cuenta(self, db):
        # Al reprogramar, la reserva no solapa consigo misma
        assert reserva_repository.existe_solapamiento(
            db, self.lab_id, self.FECHA,
            datetime.time(10, 0), datetime.time(12, 0),
            excluir_reserva_id=self.reserva_id,
        ) is False


# ============================================================
# CREAR RESERVA
# ============================================================

class TestCrearReserva:
    FECHA = datetime.date(2026, 6, 20)

    def test_crear_exitoso(self, db, laboratorio_activo):
        data = ReservaCreate(
            laboratorio_id=laboratorio_activo.laboratorio_id,
            curso="Programacion I",
            fecha=self.FECHA,
            hora_inicio=datetime.time(8, 0),
            hora_fin=datetime.time(10, 0),
        )
        reserva = reserva_service.crear_reserva(db, data, USUARIO_DOCENTE)
        assert reserva.reserva_id is not None
        assert reserva.estado == EstadoReserva.ACTIVA.value
        assert reserva.usuario_creador_id == USUARIO_DOCENTE.usuario_id

    def test_laboratorio_inexistente_lanza_404(self, db):
        data = ReservaCreate(
            laboratorio_id=9999,
            curso="Curso X",
            fecha=self.FECHA,
            hora_inicio=datetime.time(8, 0),
            hora_fin=datetime.time(10, 0),
        )
        with pytest.raises(HTTPException) as exc:
            reserva_service.crear_reserva(db, data, USUARIO_DOCENTE)
        assert exc.value.status_code == 404

    def test_laboratorio_inactivo_lanza_422(self, db, laboratorio_inactivo):
        data = ReservaCreate(
            laboratorio_id=laboratorio_inactivo.laboratorio_id,
            curso="Curso X",
            fecha=self.FECHA,
            hora_inicio=datetime.time(8, 0),
            hora_fin=datetime.time(10, 0),
        )
        with pytest.raises(HTTPException) as exc:
            reserva_service.crear_reserva(db, data, USUARIO_DOCENTE)
        assert exc.value.status_code == 422

    def test_solapamiento_lanza_409(self, db, laboratorio_activo):
        base = ReservaCreate(
            laboratorio_id=laboratorio_activo.laboratorio_id,
            curso="Reserva Base",
            fecha=self.FECHA,
            hora_inicio=datetime.time(10, 0),
            hora_fin=datetime.time(12, 0),
        )
        reserva_service.crear_reserva(db, base, USUARIO_DOCENTE)

        with pytest.raises(HTTPException) as exc:
            reserva_service.crear_reserva(db, ReservaCreate(
                laboratorio_id=laboratorio_activo.laboratorio_id,
                curso="Reserva Solapada",
                fecha=self.FECHA,
                hora_inicio=datetime.time(11, 0),
                hora_fin=datetime.time(13, 0),
            ), USUARIO_DOCENTE)
        assert exc.value.status_code == 409


# ============================================================
# CANCELAR RESERVA
# ============================================================

class TestCancelarReserva:

    def _reserva_en_db(self, db, laboratorio_id, estado=EstadoReserva.ACTIVA):
        r = Reserva(
            laboratorio_id=laboratorio_id,
            usuario_creador_id=1,
            curso="Curso Test",
            fecha=datetime.date(2026, 7, 1),
            hora_inicio=datetime.time(8, 0),
            hora_fin=datetime.time(10, 0),
            estado=estado.value,
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        return r

    def test_cancelar_exitoso(self, db, laboratorio_activo):
        reserva = self._reserva_en_db(db, laboratorio_activo.laboratorio_id)
        resultado = reserva_service.cancelar_reserva(
            db, reserva.reserva_id,
            ReservaCancelar(motivo="Mantenimiento imprevisto"),
            USUARIO_DOCENTE,
        )
        assert resultado.estado == EstadoReserva.CANCELADA.value
        assert resultado.motivo_cancelacion == "Mantenimiento imprevisto"
        assert resultado.fecha_actualizacion is not None

    def test_cancelar_ya_cancelada_lanza_422(self, db, laboratorio_activo):
        reserva = self._reserva_en_db(db, laboratorio_activo.laboratorio_id, EstadoReserva.CANCELADA)
        with pytest.raises(HTTPException) as exc:
            reserva_service.cancelar_reserva(
                db, reserva.reserva_id,
                ReservaCancelar(motivo="Intento doble"),
                USUARIO_DOCENTE,
            )
        assert exc.value.status_code == 422

    def test_cancelar_inexistente_lanza_404(self, db):
        with pytest.raises(HTTPException) as exc:
            reserva_service.cancelar_reserva(
                db, 9999,
                ReservaCancelar(motivo="No existe"),
                USUARIO_DOCENTE,
            )
        assert exc.value.status_code == 404


# ============================================================
# REPROGRAMAR RESERVA
# ============================================================

class TestReprogramarReserva:

    def _reserva_en_db(self, db, laboratorio_id, fecha, h_ini, h_fin):
        r = Reserva(
            laboratorio_id=laboratorio_id,
            usuario_creador_id=1,
            curso="Curso Test",
            fecha=fecha,
            hora_inicio=h_ini,
            hora_fin=h_fin,
            estado=EstadoReserva.ACTIVA.value,
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        return r

    def test_reprogramar_exitoso(self, db, laboratorio_activo):
        reserva = self._reserva_en_db(
            db, laboratorio_activo.laboratorio_id,
            datetime.date(2026, 7, 10),
            datetime.time(8, 0), datetime.time(10, 0),
        )
        resultado = reserva_service.reprogramar_reserva(
            db, reserva.reserva_id,
            ReservaReprogramar(
                fecha=datetime.date(2026, 7, 15),
                hora_inicio=datetime.time(14, 0),
                hora_fin=datetime.time(16, 0),
            ),
            USUARIO_DOCENTE,
        )
        assert resultado.fecha == datetime.date(2026, 7, 15)
        assert resultado.estado == EstadoReserva.REPROGRAMADA.value

    def test_reprogramar_mismo_horario_no_es_409(self, db, laboratorio_activo):
        fecha = datetime.date(2026, 7, 20)
        reserva = self._reserva_en_db(
            db, laboratorio_activo.laboratorio_id,
            fecha, datetime.time(10, 0), datetime.time(12, 0),
        )
        resultado = reserva_service.reprogramar_reserva(
            db, reserva.reserva_id,
            ReservaReprogramar(
                fecha=fecha,
                hora_inicio=datetime.time(10, 0),
                hora_fin=datetime.time(12, 0),
            ),
            USUARIO_DOCENTE,
        )
        assert resultado.estado == EstadoReserva.REPROGRAMADA.value

    def test_reprogramar_solapa_otra_lanza_409(self, db, laboratorio_activo):
        fecha = datetime.date(2026, 7, 25)
        self._reserva_en_db(
            db, laboratorio_activo.laboratorio_id,
            fecha, datetime.time(10, 0), datetime.time(12, 0),
        )
        reserva = self._reserva_en_db(
            db, laboratorio_activo.laboratorio_id,
            fecha, datetime.time(14, 0), datetime.time(16, 0),
        )
        with pytest.raises(HTTPException) as exc:
            reserva_service.reprogramar_reserva(
                db, reserva.reserva_id,
                ReservaReprogramar(
                    fecha=fecha,
                    hora_inicio=datetime.time(11, 0),
                    hora_fin=datetime.time(13, 0),
                ),
                USUARIO_DOCENTE,
            )
        assert exc.value.status_code == 409
