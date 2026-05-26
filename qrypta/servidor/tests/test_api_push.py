from fastapi.testclient import TestClient

from servidor.main import app
from servidor.api.push_api import resetear_estado_push


def _peer_hex(char: str) -> str:
    return char * 64


def test_registrar_enviar_y_baja_token_push():
    resetear_estado_push()
    cliente = TestClient(app)

    registrar = cliente.post(
        "/v1/push/registrar",
        json={"peer_id": _peer_hex("a"), "token_push": "token_valido_123"},
    )
    assert registrar.status_code == 200
    assert registrar.json()["ok"] is True

    enviar = cliente.post(
        "/v1/push/enviar",
        json={"peer_id": _peer_hex("a")},
    )
    assert enviar.status_code == 200
    assert enviar.json()["ok"] is True
    assert enviar.json()["tipo"] == "mensaje_pendiente"

    baja = cliente.post(
        "/v1/push/baja",
        json={"peer_id": _peer_hex("a")},
    )
    assert baja.status_code == 200
    assert baja.json()["ok"] is True

    enviar_sin_token = cliente.post(
        "/v1/push/enviar",
        json={"peer_id": _peer_hex("a")},
    )
    assert enviar_sin_token.status_code == 404


def test_push_valida_peer_id():
    resetear_estado_push()
    cliente = TestClient(app)

    respuesta = cliente.post(
        "/v1/push/registrar",
        json={"peer_id": "invalido", "token_push": "token_valido_123"},
    )
    assert respuesta.status_code == 422


def test_presencia_consulta_y_actualizacion():
    resetear_estado_push()
    cliente = TestClient(app)
    peer_id = _peer_hex("b")

    inicial = cliente.get(f"/v1/presencia/{peer_id}")
    assert inicial.status_code == 200
    assert inicial.json()["online"] is False

    actualizar = cliente.post(f"/v1/presencia/actualizar/{peer_id}?online=true")
    assert actualizar.status_code == 200
    assert actualizar.json()["online"] is True

    final = cliente.get(f"/v1/presencia/{peer_id}")
    assert final.status_code == 200
    assert final.json()["online"] is True
