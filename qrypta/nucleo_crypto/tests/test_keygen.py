import pytest

from nucleo_crypto.crypto import keygen


def test_generar_par_kyber_o_salta_si_falta_liboqs():
    if keygen.oqs is None:
        pytest.skip("liboqs no disponible en el entorno")

    clavePublica, clavePrivada = keygen.generarParKyber()
    assert isinstance(clavePublica, bytes)
    assert isinstance(clavePrivada, bytes)
    assert len(clavePublica) > 0
    assert len(clavePrivada) > 0


def test_generar_par_dilithium_o_salta_si_falta_liboqs():
    if keygen.oqs is None:
        pytest.skip("liboqs no disponible en el entorno")

    clavePublica, clavePrivada = keygen.generarParDilithium()
    assert isinstance(clavePublica, bytes)
    assert isinstance(clavePrivada, bytes)
    assert len(clavePublica) > 0
    assert len(clavePrivada) > 0
