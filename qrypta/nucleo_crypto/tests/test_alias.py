import pytest

from nucleo_crypto.crypto import keygen
from nucleo_crypto.identidad.alias import (
    ESTADO_ALIAS_ACTIVO,
    ESTADO_ALIAS_REVOCADO,
    actualizarAlias,
    crearAlias,
    revocarAlias,
    verificarAlias,
)


def test_ciclo_alias_crear_verificar_revocar_actualizar():
    if keygen.oqs is None:
        pytest.skip("liboqs no disponible en el entorno")

    clavePublica, clavePrivada = keygen.generarParDilithium()
    aliasActual = crearAlias("juan123", clavePrivada)

    assert aliasActual.estado == ESTADO_ALIAS_ACTIVO
    assert verificarAlias(aliasActual, clavePublica)

    aliasRevocado = revocarAlias(aliasActual, clavePrivada)
    assert aliasRevocado.estado == ESTADO_ALIAS_REVOCADO
    assert verificarAlias(aliasRevocado, clavePublica)

    aliasNuevo = actualizarAlias(aliasActual, "juan456", clavePrivada)
    assert aliasNuevo.nombre == "juan456"
    assert aliasNuevo.estado == ESTADO_ALIAS_ACTIVO
    assert verificarAlias(aliasNuevo, clavePublica)
