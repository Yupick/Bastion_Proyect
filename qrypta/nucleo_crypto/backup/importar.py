"""Importacion de backup cifrado.

Proposito: restaurar estado local desde .pqcbackup.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: importarBackup(...)
"""

from __future__ import annotations

import base64
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from argon2.low_level import Type, hash_secret_raw
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from nucleo_crypto.crypto.firma import verificar
from nucleo_crypto.identidad.alias import aliasDesdeDict
from nucleo_crypto.identidad.registro import RegistroUsuario

from .exportar import AAD_BACKUP, MAGIC_BACKUP, VERSION_BACKUP


class ErrorBackupInvalido(Exception):
    """Error cuando el backup no cumple formato o integridad."""


class ErrorContrasenaIncorrecta(Exception):
    """Error cuando la contraseña de backup no permite descifrar."""


class ErrorFirmaInvalida(Exception):
    """Error cuando la firma del checksum no es valida."""


@dataclass
class ContactoBackup:
    peerId: str
    pubkeyKyberB64: str
    pubkeyDilithiumB64: str
    aliasVerificado: bool
    fechaAgregado: str
    alias: dict[str, str] | None = None


class ListaContactosBackup:
    """Contenedor minimo para devolver contactos restaurados."""

    def __init__(self, contactos: list[dict[str, Any]]) -> None:
        self.contactos = {
            item["peerId"]: ContactoBackup(**item)
            for item in contactos
        }


def _derivarClaveBackup(contrasenaBackup: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=contrasenaBackup.encode("utf-8"),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        type=Type.ID,
    )


def _reconstruirRegistro(datos: dict[str, Any]) -> RegistroUsuario:
    aliasObjeto = None
    if isinstance(datos.get("alias"), dict):
        aliasObjeto = aliasDesdeDict(datos["alias"])

    return RegistroUsuario(
        peerId=datos["peerId"],
        pubkeyKyberB64=datos["pubkeyKyberB64"],
        privkeyKyberB64=datos["privkeyKyberB64"],
        pubkeyDilithiumB64=datos["pubkeyDilithiumB64"],
        privkeyDilithiumB64=datos["privkeyDilithiumB64"],
        alias=aliasObjeto,
        fechaCreacion=datos["fechaCreacion"],
        mnemonic24Palabras=list(datos["mnemonic24Palabras"]),
    )


def importarBackup(path: str | Path, contrasenaBackup: str) -> tuple[RegistroUsuario, ListaContactosBackup]:
    """Importa backup cifrado y devuelve registro y contactos restaurados."""
    contenido = Path(path).read_bytes()
    cursor = 0

    if contenido[:4] != MAGIC_BACKUP:
        raise ErrorBackupInvalido("Magic invalido.")
    cursor += 4

    version = struct.unpack_from("<B", contenido, cursor)[0]
    cursor += 1
    if version != VERSION_BACKUP:
        raise ErrorBackupInvalido("Version de backup no soportada.")

    if len(contenido) < cursor + 2:
        raise ErrorBackupInvalido("Backup truncado en longitud de kdf_params.")
    longitudKdf = struct.unpack_from("<H", contenido, cursor)[0]
    cursor += 2

    if len(contenido) < cursor + longitudKdf + 2 + 12 + 16 + 32:
        raise ErrorBackupInvalido("Backup truncado en parametros o checksum.")

    kdfJson = contenido[cursor : cursor + longitudKdf]
    cursor += longitudKdf
    try:
        kdfParams = json.loads(kdfJson.decode("utf-8"))
    except Exception as exc:
        raise ErrorBackupInvalido("kdf_params invalido.") from exc

    firmaLen = struct.unpack_from("<H", contenido, cursor)[0]
    cursor += 2
    if firmaLen <= 0:
        raise ErrorBackupInvalido("Longitud de firma invalida.")

    salt = base64.b64decode(kdfParams["salt_b64"])

    if len(contenido) < cursor + 12 + 16 + 32 + firmaLen:
        raise ErrorBackupInvalido("Backup demasiado pequeno para estructura minima.")

    inicioChecksum = len(contenido) - (32 + firmaLen)
    payloadCifrado = contenido[cursor:inicioChecksum]
    checksum = contenido[inicioChecksum : inicioChecksum + 32]
    firmaChecksum = contenido[inicioChecksum + 32 :]
    if len(firmaChecksum) != firmaLen:
        raise ErrorBackupInvalido("Longitud real de firma no coincide con cabecera.")

    checksumCalculado = hashlib.blake2b(payloadCifrado, digest_size=32).digest()
    if checksum != checksumCalculado:
        raise ErrorBackupInvalido("Checksum invalido.")

    if len(payloadCifrado) < 12 + 16:
        raise ErrorBackupInvalido("Payload cifrado invalido.")

    nonce = payloadCifrado[:12]
    cifradoCompleto = payloadCifrado[12:]

    try:
        clave = _derivarClaveBackup(contrasenaBackup, salt)
        plano = AESGCM(clave).decrypt(nonce, cifradoCompleto, AAD_BACKUP)
    except InvalidTag as exc:
        raise ErrorContrasenaIncorrecta("Contrasena incorrecta o backup alterado.") from exc
    except Exception as exc:
        raise ErrorBackupInvalido("No se pudo descifrar el backup.") from exc

    try:
        payload = json.loads(plano.decode("utf-8"))
    except Exception as exc:
        raise ErrorBackupInvalido("Payload JSON invalido.") from exc

    if "registro" not in payload or "contactos" not in payload:
        raise ErrorBackupInvalido("Estructura de payload incompleta.")

    registro = _reconstruirRegistro(payload["registro"])
    contactos = ListaContactosBackup(payload["contactos"])

    clavePublica = base64.b64decode(registro.pubkeyDilithiumB64)
    if not verificar(checksum, firmaChecksum, clavePublica):
        raise ErrorFirmaInvalida("La firma del checksum es invalida.")

    return registro, contactos
