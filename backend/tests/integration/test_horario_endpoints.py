import pytest
from datetime import time, date

from app.models.usuario import Usuario
from app.models.horario import HorarioLaboratorio
from app.security.dependencies import get_current_user, UsuarioActual
from app.main import app
from app.config.db import get_db
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures de usuario/token con rol COORDINADOR (horarios lo requiere)
# ---------------------------------------------------------------------------

@pytest.fixture()
def usuario_coordinador(db):
    from app.services.auth_service import hash_password
    u = Usuario(
        email="coord@uni.edu",
        password_hash=hash_password("coord1234"),
        rol="COORDINADOR",
        activo=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture()
def token_coordinador(client, usuario_coordinador):
    resp = client.post("/auth/login", json={
        "email": usuario_coordinador.email,
        "password": "coord1234",
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture()
def horario_en_db(db, laboratorio_activo):
    """Horario disponible insertado directamente en BD."""
    h = HorarioLaboratorio(
        laboratorio_id=laboratorio_activo.laboratorio_id,
        dia_semana=1,
        hora_inicio=time(8, 0),
        hora_fin=time(12, 0),
        disponible=True,
        fecha_bloqueo=None,
        motivo_bloqueo=None,
    )
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


@pytest.fixture()
def horario_bloqueado_en_db(db, laboratorio_activo):
    """Horario ya bloqueado insertado directamente en BD."""
    h = HorarioLaboratorio(
        laboratorio_id=laboratorio_activo.laboratorio_id,
        dia_semana=3,
        hora_inicio=time(14, 0),
        hora_fin=time(18, 0),
        disponible=False,
        fecha_bloqueo=date(2026, 12, 25),
        motivo_bloqueo="Festivo navidad",
    )
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


@pytest.fixture()
def client_docente(db):
    """Cliente con rol DOCENTE (no puede crear/modificar horarios)."""
    def override_db():
        yield db

    def override_user():
        return UsuarioActual(usuario_id=99, email="doc@test.com", rol="DOCENTE")

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _payload_crear(laboratorio_id: int) -> dict:
    return {
        "laboratorio_id": laboratorio_id,
        "dia_semana": 2,
        "hora_inicio": "09:00:00",
        "hora_fin": "13:00:00",
    }


# ============================================================
# POST /horarios/
# ============================================================

class TestCrearHorarioEndpoint:

    def test_crear_exitoso_devuelve_201(self, client, laboratorio_activo, token_coordinador):
        resp = client.post(
            "/horarios/",
            json=_payload_crear(laboratorio_activo.laboratorio_id),
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["dia_semana"] == 2
        assert body["disponible"] is True
        assert "horario_id" in body

    def test_crear_sin_token_devuelve_401(self, client, laboratorio_activo):
        resp = client.post("/horarios/", json=_payload_crear(laboratorio_activo.laboratorio_id))
        assert resp.status_code == 401

    def test_crear_rol_docente_devuelve_403(self, client_docente, laboratorio_activo):
        resp = client_docente.post(
            "/horarios/",
            json=_payload_crear(laboratorio_activo.laboratorio_id),
        )
        assert resp.status_code == 403

    def test_crear_laboratorio_inexistente_devuelve_404(self, client, token_coordinador):
        resp = client.post(
            "/horarios/",
            json=_payload_crear(9999),
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 404

    def test_crear_laboratorio_inactivo_devuelve_400(self, client, laboratorio_inactivo, token_coordinador):
        resp = client.post(
            "/horarios/",
            json=_payload_crear(laboratorio_inactivo.laboratorio_id),
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 400

    def test_crear_horario_duplicado_devuelve_409(self, client, laboratorio_activo, horario_en_db, token_coordinador):
        payload = {
            "laboratorio_id": laboratorio_activo.laboratorio_id,
            "dia_semana": horario_en_db.dia_semana,
            "hora_inicio": "09:00:00",
            "hora_fin": "11:00:00",
        }
        resp = client.post(
            "/horarios/",
            json=payload,
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 409


# ============================================================
# GET /horarios/laboratorio/{laboratorio_id}
# ============================================================

class TestListarHorariosEndpoint:

    def test_listar_exitoso_devuelve_200(self, client, laboratorio_activo, horario_en_db, token_admin):
        resp = client.get(
            f"/horarios/laboratorio/{laboratorio_activo.laboratorio_id}",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) >= 1

    def test_listar_sin_token_devuelve_401(self, client, laboratorio_activo):
        resp = client.get(f"/horarios/laboratorio/{laboratorio_activo.laboratorio_id}")
        assert resp.status_code == 401

    def test_listar_laboratorio_inexistente_devuelve_404(self, client, token_admin):
        resp = client.get(
            "/horarios/laboratorio/9999",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert resp.status_code == 404

    def test_listar_laboratorio_sin_horarios_devuelve_lista_vacia(self, client, laboratorio_activo, token_admin):
        resp = client.get(
            f"/horarios/laboratorio/{laboratorio_activo.laboratorio_id}",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert resp.status_code == 200
        assert resp.json() == []


# ============================================================
# GET /horarios/{horario_id}
# ============================================================

class TestObtenerHorarioEndpoint:

    def test_obtener_exitoso_devuelve_200(self, client, horario_en_db, token_admin):
        resp = client.get(
            f"/horarios/{horario_en_db.horario_id}",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["horario_id"] == horario_en_db.horario_id

    def test_obtener_sin_token_devuelve_401(self, client, horario_en_db):
        resp = client.get(f"/horarios/{horario_en_db.horario_id}")
        assert resp.status_code == 401

    def test_obtener_inexistente_devuelve_404(self, client, token_admin):
        resp = client.get(
            "/horarios/9999",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert resp.status_code == 404


# ============================================================
# PUT /horarios/{horario_id}
# ============================================================

class TestActualizarHorarioEndpoint:

    def test_actualizar_exitoso_devuelve_200(self, client, horario_en_db, token_coordinador):
        resp = client.put(
            f"/horarios/{horario_en_db.horario_id}",
            json={"hora_inicio": "10:00:00", "hora_fin": "14:00:00"},
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["hora_inicio"] == "10:00:00"

    def test_actualizar_sin_token_devuelve_401(self, client, horario_en_db):
        resp = client.put(
            f"/horarios/{horario_en_db.horario_id}",
            json={"hora_inicio": "10:00:00", "hora_fin": "14:00:00"},
        )
        assert resp.status_code == 401

    def test_actualizar_rol_docente_devuelve_403(self, client_docente, horario_en_db):
        resp = client_docente.put(
            f"/horarios/{horario_en_db.horario_id}",
            json={"hora_inicio": "10:00:00", "hora_fin": "14:00:00"},
        )
        assert resp.status_code == 403

    def test_actualizar_inexistente_devuelve_404(self, client, token_coordinador):
        resp = client.put(
            "/horarios/9999",
            json={"hora_inicio": "10:00:00", "hora_fin": "14:00:00"},
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 404


# ============================================================
# PATCH /horarios/{horario_id}/bloquear
# ============================================================

class TestBloquearFechaEndpoint:

    def test_bloquear_exitoso_devuelve_200(self, client, horario_en_db, token_coordinador):
        resp = client.patch(
            f"/horarios/{horario_en_db.horario_id}/bloquear",
            json={"fecha_bloqueo": "2026-12-25", "motivo_bloqueo": "Festivo navidad"},
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["disponible"] is False
        assert body["motivo_bloqueo"] == "Festivo navidad"

    def test_bloquear_sin_token_devuelve_401(self, client, horario_en_db):
        resp = client.patch(
            f"/horarios/{horario_en_db.horario_id}/bloquear",
            json={"fecha_bloqueo": "2026-12-25", "motivo_bloqueo": "Festivo navidad"},
        )
        assert resp.status_code == 401

    def test_bloquear_ya_bloqueado_misma_fecha_devuelve_409(self, client, horario_bloqueado_en_db, token_coordinador):
        resp = client.patch(
            f"/horarios/{horario_bloqueado_en_db.horario_id}/bloquear",
            json={"fecha_bloqueo": "2026-12-25", "motivo_bloqueo": "Festivo navidad"},
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 409

    def test_bloquear_inexistente_devuelve_404(self, client, token_coordinador):
        resp = client.patch(
            "/horarios/9999/bloquear",
            json={"fecha_bloqueo": "2026-12-25", "motivo_bloqueo": "Festivo"},
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 404


# ============================================================
# PATCH /horarios/{horario_id}/disponible
# ============================================================

class TestDesbloquearHorarioEndpoint:

    def test_desbloquear_exitoso_devuelve_200(self, client, horario_bloqueado_en_db, token_coordinador):
        resp = client.patch(
            f"/horarios/{horario_bloqueado_en_db.horario_id}/disponible",
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["disponible"] is True
        assert body["fecha_bloqueo"] is None

    def test_desbloquear_sin_token_devuelve_401(self, client, horario_bloqueado_en_db):
        resp = client.patch(f"/horarios/{horario_bloqueado_en_db.horario_id}/disponible")
        assert resp.status_code == 401

    def test_desbloquear_ya_disponible_devuelve_400(self, client, horario_en_db, token_coordinador):
        resp = client.patch(
            f"/horarios/{horario_en_db.horario_id}/disponible",
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 400

    def test_desbloquear_inexistente_devuelve_404(self, client, token_coordinador):
        resp = client.patch(
            "/horarios/9999/disponible",
            headers={"Authorization": f"Bearer {token_coordinador}"},
        )
        assert resp.status_code == 404
