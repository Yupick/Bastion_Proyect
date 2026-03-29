from datetime import UTC, datetime

from fastapi.testclient import TestClient

from servidor.config.settings import settings
from servidor.main import app
from servidor.api import rutas


def _mensaje_valido() -> dict:
    return {
        "peerIdOrigen": "a" * 64,
        "peerIdDestino": "b" * 64,
        "payloadCifradoB64": "cGF5bG9hZA==",
        "timestamp": datetime.now(UTC).isoformat(),
        "firmaB64": "ZmlybWE=",
    }


def test_enviar_y_recuperar_y_luego_vacio():
    rutas.resetearAlmacenMensajes()
    cliente = TestClient(app)

    r1 = cliente.post("/v1/mensaje", json=_mensaje_valido())
    assert r1.status_code == 200

    r2 = cliente.get(f"/v1/mensajes/{'b' * 64}")
    assert r2.status_code == 200
    assert len(r2.json()) == 1

    r3 = cliente.get(f"/v1/mensajes/{'b' * 64}")
    assert r3.status_code == 200
    assert r3.json() == []


def test_peer_id_invalido_rechazado():
    rutas.resetearAlmacenMensajes()
    cliente = TestClient(app)

    mensaje = _mensaje_valido()
    mensaje["peerIdDestino"] = "invalido"

    respuesta = cliente.post("/v1/mensaje", json=mensaje)
    assert respuesta.status_code == 422


def test_campos_faltantes_rechazados():
    rutas.resetearAlmacenMensajes()
    cliente = TestClient(app)

    respuesta = cliente.post("/v1/mensaje", json={"peerIdOrigen": "a" * 64})
    assert respuesta.status_code == 422


def test_admin_limpiar_mensajes_exige_token():
    rutas.resetearAlmacenMensajes()
    cliente = TestClient(app)

    cliente.post("/v1/mensaje", json=_mensaje_valido())

    sinToken = cliente.delete("/v1/admin/mensajes")
    assert sinToken.status_code == 401

    conToken = cliente.delete(
        "/v1/admin/mensajes",
        headers={"X-Admin-Token": settings.adminToken},
    )
    assert conToken.status_code == 200

    consulta = cliente.get(f"/v1/mensajes/{'b' * 64}")
    assert consulta.status_code == 200
    assert consulta.json() == []
