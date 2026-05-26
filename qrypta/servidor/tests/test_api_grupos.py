from fastapi.testclient import TestClient

from servidor.api.grupos_api import resetear_estado_grupos_api
from servidor.main import app


ADMIN = "a" * 64
MIEMBRO = "b" * 64
OTRO = "c" * 64


def _crear_grupo(cliente: TestClient) -> None:
    respuesta = cliente.post(
        "/v1/grupos/crear",
        json={
            "grupo_id": "grupo-beta",
            "admin": ADMIN,
            "miembros": [MIEMBRO],
            "clave_grupo": "clave_inicial_segura",
        },
    )
    assert respuesta.status_code == 200


def test_crear_agregar_mensaje_y_consultar_miembros():
    resetear_estado_grupos_api()
    cliente = TestClient(app)
    _crear_grupo(cliente)

    agregar = cliente.post(
        "/v1/grupos/agregar_miembro",
        json={"grupo_id": "grupo-beta", "admin": ADMIN, "miembro": OTRO},
    )
    assert agregar.status_code == 200
    assert OTRO in agregar.json()["miembros"]

    mensaje = cliente.post(
        "/v1/grupos/mensaje",
        json={
            "grupo_id": "grupo-beta",
            "remitente": OTRO,
            "payload_cifrado": "c2ludGV4dF9jaWZyYWRv",
        },
    )
    assert mensaje.status_code == 200
    assert mensaje.json()["mensaje"]["remitente"] == OTRO

    miembros = cliente.get("/v1/grupos/grupo-beta/miembros")
    assert miembros.status_code == 200
    assert miembros.json()["grupo_id"] == "grupo-beta"
    assert ADMIN in miembros.json()["miembros"]
    assert MIEMBRO in miembros.json()["miembros"]
    assert OTRO in miembros.json()["miembros"]

    mensajes = cliente.get("/v1/grupos/grupo-beta/mensajes")
    assert mensajes.status_code == 200
    assert len(mensajes.json()) == 1


def test_remover_miembro_rotando_clave_desautoriza_mensaje():
    resetear_estado_grupos_api()
    cliente = TestClient(app)
    _crear_grupo(cliente)

    remover = cliente.post(
        "/v1/grupos/remover_miembro",
        json={
            "grupo_id": "grupo-beta",
            "admin": ADMIN,
            "miembro": MIEMBRO,
            "nueva_clave": "clave_rotada_segura",
        },
    )
    assert remover.status_code == 200
    assert MIEMBRO not in remover.json()["miembros"]

    mensaje = cliente.post(
        "/v1/grupos/mensaje",
        json={
            "grupo_id": "grupo-beta",
            "remitente": MIEMBRO,
            "payload_cifrado": "ZG9jdW1lbnRv",
        },
    )
    assert mensaje.status_code == 403


def test_agregar_miembro_exige_admin():
    resetear_estado_grupos_api()
    cliente = TestClient(app)
    _crear_grupo(cliente)

    respuesta = cliente.post(
        "/v1/grupos/agregar_miembro",
        json={"grupo_id": "grupo-beta", "admin": OTRO, "miembro": OTRO},
    )
    assert respuesta.status_code == 403


def test_crear_grupo_duplicado_rechazado():
    resetear_estado_grupos_api()
    cliente = TestClient(app)
    _crear_grupo(cliente)

    duplicado = cliente.post(
        "/v1/grupos/crear",
        json={
            "grupo_id": "grupo-beta",
            "admin": ADMIN,
            "miembros": [MIEMBRO],
            "clave_grupo": "clave_inicial_segura",
        },
    )
    assert duplicado.status_code == 400
