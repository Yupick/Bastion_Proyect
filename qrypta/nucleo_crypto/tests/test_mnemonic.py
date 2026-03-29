import pytest

from nucleo_crypto.recuperacion import mnemonic


def test_mnemonic_roundtrip_y_derivacion():
    if mnemonic.Mnemonic is None or mnemonic.hash_secret_raw is None:
        pytest.skip("Dependencias mnemonic/argon2 no disponibles")

    entropia, palabras = mnemonic.generarMnemonic()
    entropiaRecuperada = mnemonic.recuperarDesde(palabras)
    clave = mnemonic.derivarClaveDesdeEntropia(entropia)

    assert len(palabras) == 24
    assert entropia == entropiaRecuperada
    assert isinstance(clave, bytes)
    assert len(clave) == 32
