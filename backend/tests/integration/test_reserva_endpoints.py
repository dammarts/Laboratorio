import datetime
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config.db import get_db
from app.security.dependencies import get_current_user, UsuarioActual
from app.models.reserva import Reserva, EstadoReserva


@pytest.fixture()
def client_consulta(db):
    """Cliente autenticado con rol CONSULTA (para probar 403)."""
    def override_db():
        yield db

    def override_usuario():
        return UsuarioActual(usuario_id=3, email="consulta@test.com", rol="CONSULTA")

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_usuario
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _payload_crear(laboratorio_id: int, fecha: str = "2026-08-01") -> dict:
    return {
        "laboratorio_id": laboratorio_id,
        "curso": "Programacion I",
        "fecha": fecha,
        "hora_inicio": "08:00:00",
        "hora_fin": "10:00:00",
    }


# ============================================================
# POST /reservas
# ============================================================

class TestCrearReservaEndpoint:

    def test_crear_exitoso_devuelve_201(self, client, laboratorio_activo, token_admin):
        resp = client.post("/reservas/", json=_payload_crear(laboratorio_activo.laboratorio_id),
                           headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["estado"] == "ACTIVA"
        assert body["curso"] == "Programacion I"
        assert "reserva_id" in body

    def test_crear_sin_token_devuelve_401(self, client):
        resp = client.post("/reservas/", json=_payload_crear(1))
        assert resp.status_code == 401

    def test_crear_rol_consulta_devuelve_403(self, client_consulta, laboratorio_activo):
        resp = client_consulta.post(
            "/reservas/",
            json=_payload_crear(laboratorio_activo.laboratorio_id),
            headers={"Authorization": "Bearer cualquier-token"},
        )
        assert resp.status_code == 403

    def test_crear_laboratorio_inexistente_devuelve_404(self, client, token_admin):
        resp = client.post("/reservas/", json=_payload_crear(9999),
                           headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 404

    def test_crear_laboratorio_inactivo_devuelve_422(self, client, laboratorio_inactivo, token_admin):
        resp = client.post("/reservas/", json=_payload_crear(laboratorio_inactivo.laboratorio_id),
                           headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 422

    def test_crear_solapamiento_devuelve_409(self, client, laboratorio_activo, token_admin):
        payload = _payload_crear(laboratorio_activo.laboratorio_id, "2026-08-05")
        client.post("/reservas/", json=payload,
                    headers={"Authorization": f"Bearer {token_admin}"})
        resp = client.post("/reservas/",
                           json={**payload, "hora_inicio": "09:00:00", "hora_fin": "11:00:00"},
                           headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 409


# ============================================================
# GET /reservas y GET /reservas/{id}
# ============================================================

class TestListarObtenerEndpoint:

    def test_listar_devuelve_200(self, client, token_admin):
        resp = client.get("/reservas/", headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_listar_sin_token_devuelve_401(self, client):
        resp = client.get("/reservas/")
        assert resp.status_code == 401

    def test_obtener_existente_devuelve_200(self, client, laboratorio_activo, token_admin):
        creada = client.post("/reservas/",
                             json=_payload_crear(laboratorio_activo.laboratorio_id, "2026-08-10"),
                             headers={"Authorization": f"Bearer {token_admin}"})
        reserva_id = creada.json()["reserva_id"]
        resp = client.get(f"/reservas/{reserva_id}",
                          headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 200
        assert resp.json()["reserva_id"] == reserva_id

    def test_obtener_inexistente_devuelve_404(self, client, token_admin):
        resp = client.get("/reservas/9999",
                          headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 404


# ============================================================
# PATCH /reservas/{id}/cancelar
# ============================================================

class TestCancelarEndpoint:

    def _crear_reserva(self, client, token_admin: str, laboratorio_id: int, fecha: str) -> int:
        resp = client.post("/reservas/", json=_payload_crear(laboratorio_id, fecha),
                           headers={"Authorization": f"Bearer {token_admin}"})
        return resp.json()["reserva_id"]

    def test_cancelar_exitoso_devuelve_200(self, client, laboratorio_activo, token_admin):
        rid = self._crear_reserva(client, token_admin, laboratorio_activo.laboratorio_id, "2026-09-01")
        resp = client.patch(f"/reservas/{rid}/cancelar",
                            json={"motivo": "Festivo nacional"},
                            headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 200
        assert resp.json()["estado"] == "CANCELADA"
        assert resp.json()["motivo_cancelacion"] == "Festivo nacional"

    def test_cancelar_sin_motivo_devuelve_422(self, client, laboratorio_activo, token_admin):
        rid = self._crear_reserva(client, token_admin, laboratorio_activo.laboratorio_id, "2026-09-02")
        resp = client.patch(f"/reservas/{rid}/cancelar",
                            json={"motivo": ""},
                            headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 422

    def test_cancelar_inexistente_devuelve_404(self, client, token_admin):
        resp = client.patch("/reservas/9999/cancelar",
                            json={"motivo": "No existe"},
                            headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 404


# ============================================================
# PATCH /reservas/{id}/reprogramar
# ============================================================

class TestReprogramarEndpoint:

    def _crear_reserva(self, client, token_admin: str, laboratorio_id: int, fecha: str,
                       h_ini: str = "08:00:00", h_fin: str = "10:00:00") -> int:
        resp = client.post("/reservas/", json={
            "laboratorio_id": laboratorio_id,
            "curso": "Curso Test",
            "fecha": fecha,
            "hora_inicio": h_ini,
            "hora_fin": h_fin,
        }, headers={"Authorization": f"Bearer {token_admin}"})
        return resp.json()["reserva_id"]

    def test_reprogramar_exitoso_devuelve_200(self, client, laboratorio_activo, token_admin):
        rid = self._crear_reserva(client, token_admin, laboratorio_activo.laboratorio_id, "2026-09-10")
        resp = client.patch(f"/reservas/{rid}/reprogramar", json={
            "fecha": "2026-09-20",
            "hora_inicio": "14:00:00",
            "hora_fin": "16:00:00",
        }, headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 200
        assert resp.json()["estado"] == "REPROGRAMADA"
        assert resp.json()["fecha"] == "2026-09-20"

    def test_reprogramar_mismo_horario_devuelve_200(self, client, laboratorio_activo, token_admin):
        rid = self._crear_reserva(client, token_admin, laboratorio_activo.laboratorio_id,
                                  "2026-09-15", "10:00:00", "12:00:00")
        resp = client.patch(f"/reservas/{rid}/reprogramar", json={
            "fecha": "2026-09-15",
            "hora_inicio": "10:00:00",
            "hora_fin": "12:00:00",
        }, headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 200

    def test_reprogramar_solapamiento_devuelve_409(self, client, laboratorio_activo, token_admin):
        fecha = "2026-09-25"
        self._crear_reserva(client, token_admin, laboratorio_activo.laboratorio_id,
                            fecha, "10:00:00", "12:00:00")
        rid = self._crear_reserva(client, token_admin, laboratorio_activo.laboratorio_id,
                                  fecha, "14:00:00", "16:00:00")
        resp = client.patch(f"/reservas/{rid}/reprogramar", json={
            "fecha": fecha,
            "hora_inicio": "11:00:00",
            "hora_fin": "13:00:00",
        }, headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 409


# ============================================================
# GET /reservas/historial
# ============================================================

class TestHistorialEndpoint:

    def _crear_y_cancelar(self, client, token_admin: str, laboratorio_id: int, fecha: str) -> int:
        resp = client.post("/reservas/", json=_payload_crear(laboratorio_id, fecha),
                           headers={"Authorization": f"Bearer {token_admin}"})
        rid = resp.json()["reserva_id"]
        client.patch(f"/reservas/{rid}/cancelar",
                     json={"motivo": "Test historial"},
                     headers={"Authorization": f"Bearer {token_admin}"})
        return rid

    def test_listar_historial_devuelve_200(self, client, laboratorio_activo, token_admin):
        self._crear_y_cancelar(client, token_admin, laboratorio_activo.laboratorio_id, "2026-10-01")
        resp = client.get("/reservas/historial",
                          headers={"Authorization": f"Bearer {token_admin}"})
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_filtrar_por_laboratorio_id(self, client, laboratorio_activo, token_admin):
        self._crear_y_cancelar(client, token_admin, laboratorio_activo.laboratorio_id, "2026-10-05")
        resp = client.get(
            f"/reservas/historial?laboratorio_id={laboratorio_activo.laboratorio_id}",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert resp.status_code == 200
        assert all(isinstance(h["historial_id"], int) for h in resp.json())

    def test_filtrar_por_fecha_desde_hasta(self, client, laboratorio_activo, token_admin):
        self._crear_y_cancelar(client, token_admin, laboratorio_activo.laboratorio_id, "2026-10-10")
        resp = client.get(
            "/reservas/historial?fecha_desde=2026-10-01&fecha_hasta=2026-10-31",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert resp.status_code == 200
