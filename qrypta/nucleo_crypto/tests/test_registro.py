import pytest

from nucleo_crypto.crypto import keygen
from nucleo_crypto.identidad.registro import exportarClavePublica, importarContacto, registrarNuevoUsuario


def test_registro_y_exportacion_importacion_con_alias(monkeypatch):
    if keygen.oqs is None:
        pytest.skip("liboqs no disponible en el entorno")

    monkeypatch.setattr(
        "nucleo_crypto.identidad.registro.guardarRegistroLocal",
        lambda registro, contrasena: None,
    )

    registro = registrarNuevoUsuario("clave-segura", aliasNombre="demo")
    datosPublicos = exportarClavePublica(registro)
    contacto = importarContacto(datosPublicos)

    assert registro.peerId == contacto["peerId"]
    assert "alias" in datosPublicos
    assert contacto["pubkeyKyberB64"] == registro.pubkeyKyberB64
