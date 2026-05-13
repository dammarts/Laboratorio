# Tests de humo: verifican que el sistema arrancó y los endpoints
# principales responden. Deben correr en < 5 segundos.
#
# Ejecutar: pytest tests/smoke/ -v -m smoke

import pytest


@pytest.mark.smoke
def test_health_check_retorna_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


@pytest.mark.smoke
def test_swagger_disponible(client):
    resp = client.get("/docs")
    assert resp.status_code == 200


@pytest.mark.smoke
def test_login_invalido_retorna_401(client):
    resp = client.post("/auth/login", json={
        "email": "noexiste@uni.edu",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


@pytest.mark.smoke
def test_laboratorios_publico_retorna_200(client):
    # /laboratorios es un endpoint público — confirma que el sistema responde
    resp = client.get("/laboratorios")
    assert resp.status_code == 200


@pytest.mark.smoke
def test_reservas_sin_token_retorna_401(client):
    resp = client.get("/reservas/")
    assert resp.status_code == 401


@pytest.mark.smoke
def test_reportes_sin_token_retorna_401(client):
    resp = client.get("/reportes/uso-laboratorio")
    assert resp.status_code == 401


@pytest.mark.smoke
def test_horarios_endpoint_disponible(client):
    # GET /horarios/laboratorio/{id} es la ruta válida; 200 o 404 confirman que está vivo
    resp = client.get("/horarios/laboratorio/1")
    assert resp.status_code != 405


@pytest.mark.smoke
def test_usuarios_sin_token_retorna_401(client):
    resp = client.get("/usuarios")
    assert resp.status_code == 401


@pytest.mark.smoke
def test_reportes_docente_sin_token_retorna_401(client):
    resp = client.get("/reportes/por-docente")
    assert resp.status_code == 401


@pytest.mark.smoke
def test_reportes_ocupacion_sin_token_retorna_401(client):
    resp = client.get("/reportes/ocupacion-mensual?mes=1&anio=2024")
    assert resp.status_code == 401
