import pytest

from nucleo_crypto.almacenamiento import local


def test_guardar_y_cargar_identidad_roundtrip(tmp_path):
    if local.hash_secret_raw is None or local.AESGCM is None:
        pytest.skip("Dependencias argon2/cryptography no disponibles")

    ruta = tmp_path / "identidad.enc"
    datos = {"peerId": "abc", "alias": "demo"}

    local.guardarIdentidad(datos, "clave-segura", ruta=ruta)
    datosRecuperados = local.cargarIdentidad("clave-segura", ruta=ruta)

    assert datosRecuperados == datos


def test_falla_si_checksum_no_coincide(tmp_path):
    if local.hash_secret_raw is None or local.AESGCM is None:
        pytest.skip("Dependencias argon2/cryptography no disponibles")

    ruta = tmp_path / "identidad.enc"
    local.guardarIdentidad({"peerId": "abc"}, "clave-segura", ruta=ruta)

    contenido = ruta.read_text(encoding="utf-8")
    contenidoAlterado = contenido.replace("A", "B", 1)
    ruta.write_text(contenidoAlterado, encoding="utf-8")

    with pytest.raises(Exception):
        local.cargarIdentidad("clave-segura", ruta=ruta)
