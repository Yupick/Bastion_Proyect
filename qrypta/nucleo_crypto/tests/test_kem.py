import pytest

from nucleo_crypto.crypto import kem, keygen


def test_encapsular_desencapsular_comparten_secreto():
    if keygen.oqs is None:
        pytest.skip("liboqs no disponible en el entorno")

    clavePublica, clavePrivada = keygen.generarParKyber()
    textoCifrado, secretoA = kem.encapsular(clavePublica)
    secretoB = kem.desencapsular(clavePrivada, textoCifrado)

    assert secretoA == secretoB
    assert len(secretoA) > 0
