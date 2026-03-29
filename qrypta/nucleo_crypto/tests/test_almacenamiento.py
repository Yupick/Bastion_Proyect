import pytest
import json

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

    estructura = json.loads(ruta.read_text(encoding="utf-8"))
    checksumOriginal = estructura["checksum_b64"]
    estructura["checksum_b64"] = (
        ("A" if checksumOriginal[0] != "A" else "B") + checksumOriginal[1:]
    )
    ruta.write_text(json.dumps(estructura), encoding="utf-8")

    with pytest.raises(Exception):
        local.cargarIdentidad("clave-segura", ruta=ruta)
