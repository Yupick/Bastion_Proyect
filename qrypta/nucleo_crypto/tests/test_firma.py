import pytest

from nucleo_crypto.crypto import firma, keygen


def test_firma_valida_y_rechaza_mensaje_alterado():
    if keygen.oqs is None:
        pytest.skip("liboqs no disponible en el entorno")

    clavePublica, clavePrivada = keygen.generarParDilithium()
    mensaje = b"qrypta-mensaje"
    firmaDigital = firma.firmar(mensaje, clavePrivada)

    assert firma.verificar(mensaje, firmaDigital, clavePublica)
    assert not firma.verificar(mensaje + b"-alterado", firmaDigital, clavePublica)
