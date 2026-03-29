import struct

import pytest

from nucleo_crypto.backup.exportar import exportarBackup
from nucleo_crypto.backup.importar import (
    ErrorBackupInvalido,
    ErrorContrasenaIncorrecta,
    ErrorFirmaInvalida,
    importarBackup,
)
from nucleo_crypto.contactos.lista import ListaContactos
from nucleo_crypto.crypto import keygen
from nucleo_crypto.identidad.registro import exportarClavePublica, registrarNuevoUsuario


def _crearEscenario(monkeypatch):
    monkeypatch.setattr(
        "nucleo_crypto.identidad.registro.guardarRegistroLocal",
        lambda registro, contrasena: None,
    )
    registro = registrarNuevoUsuario("clave-local", aliasNombre="usuario_demo")
    lista = ListaContactos()
    lista.agregarContacto(exportarClavePublica(registro))
    return registro, lista


def _offset_checksum(contenido: bytes) -> int:
    cursor = 0
    cursor += 4  # magic
    cursor += 1  # version
    kdf_len = struct.unpack_from("<H", contenido, cursor)[0]
    cursor += 2 + kdf_len
    firma_len = struct.unpack_from("<H", contenido, cursor)[0]
    cursor += 2
    return len(contenido) - (32 + firma_len)


def test_backup_roundtrip(monkeypatch, tmp_path):
    if keygen.oqs is None:
        pytest.skip("liboqs no disponible en el entorno")

    registro, lista = _crearEscenario(monkeypatch)
    ruta = tmp_path / "respaldo.pqcbackup"

    exportarBackup(registro, lista, "contrasena-backup", ruta)
    registroRecuperado, contactosRecuperados = importarBackup(ruta, "contrasena-backup")

    assert registroRecuperado.peerId == registro.peerId
    assert len(contactosRecuperados.contactos) == 1


def test_backup_falla_con_contrasena_incorrecta(monkeypatch, tmp_path):
    if keygen.oqs is None:
        pytest.skip("liboqs no disponible en el entorno")

    registro, lista = _crearEscenario(monkeypatch)
    ruta = tmp_path / "respaldo.pqcbackup"

    exportarBackup(registro, lista, "contrasena-correcta", ruta)

    with pytest.raises(ErrorContrasenaIncorrecta):
        importarBackup(ruta, "contrasena-incorrecta")


def test_backup_falla_si_checksum_alterado(monkeypatch, tmp_path):
    if keygen.oqs is None:
        pytest.skip("liboqs no disponible en el entorno")

    registro, lista = _crearEscenario(monkeypatch)
    ruta = tmp_path / "respaldo.pqcbackup"

    exportarBackup(registro, lista, "contrasena-backup", ruta)
    contenido = bytearray(ruta.read_bytes())

    idx = _offset_checksum(contenido)
    contenido[idx] ^= 0x01
    ruta.write_bytes(bytes(contenido))

    with pytest.raises(ErrorFirmaInvalida):
        importarBackup(ruta, "contrasena-backup")


def test_backup_falla_si_firma_alterada(monkeypatch, tmp_path):
    if keygen.oqs is None:
        pytest.skip("liboqs no disponible en el entorno")

    registro, lista = _crearEscenario(monkeypatch)
    ruta = tmp_path / "respaldo.pqcbackup"

    exportarBackup(registro, lista, "contrasena-backup", ruta)
    contenido = bytearray(ruta.read_bytes())

    contenido[-1] ^= 0x01
    ruta.write_bytes(bytes(contenido))

    with pytest.raises(ErrorBackupInvalido):
        importarBackup(ruta, "contrasena-backup")
