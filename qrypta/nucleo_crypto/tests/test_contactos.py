import base64

import pytest

from nucleo_crypto.contactos.lista import ListaContactos, verificarMensaje
from nucleo_crypto.crypto import firma, keygen
from nucleo_crypto.identidad.registro import exportarClavePublica, registrarNuevoUsuario


def test_agregar_buscar_y_verificar_mensaje(monkeypatch):
    if keygen.oqs is None:
        pytest.skip("liboqs no disponible en el entorno")

    monkeypatch.setattr(
        "nucleo_crypto.identidad.registro.guardarRegistroLocal",
        lambda registro, contrasena: None,
    )

    registro = registrarNuevoUsuario("clave-segura", aliasNombre="pepe")
    lista = ListaContactos()
    contacto = lista.agregarContacto(exportarClavePublica(registro))

    assert lista.buscarPorPeerId(contacto.peerId) is not None

    mensaje = b"hola-qrypta"
    firmaB64 = base64.b64encode(
        firma.firmar(mensaje, base64.b64decode(registro.privkeyDilithiumB64))
    ).decode("ascii")

    assert verificarMensaje(mensaje, firmaB64, contacto.peerId, lista)
