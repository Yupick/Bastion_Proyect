"""Exportacion de backup cifrado.

Proposito: generar archivo .pqcbackup.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: exportarBackup(...)
"""

from __future__ import annotations

import json
import os
import struct
import base64
import hashlib
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from argon2.low_level import Type, hash_secret_raw
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from nucleo_crypto.crypto.firma import firmar

MAGIC_BACKUP = b"BSTN"
VERSION_BACKUP = 1
AAD_BACKUP = b"qrypta-backup-v1"


def _serializarRegistro(registro: Any) -> dict[str, Any]:
    if is_dataclass(registro):
        return asdict(registro)
    if isinstance(registro, dict):
        return registro
    raise TypeError("registro debe ser dataclass o dict.")


def _serializarContactos(contactos: Any) -> list[dict[str, Any]]:
    if hasattr(contactos, "contactos") and isinstance(contactos.contactos, dict):
        return [
            asdict(contacto) if is_dataclass(contacto) else contacto
            for contacto in contactos.contactos.values()
        ]
    if isinstance(contactos, list):
        return contactos
    raise TypeError("contactos debe ser ListaContactos o list[dict].")


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


def exportarBackup(
    registro: Any,
    contactos: Any,
    contrasenaBackup: str,
    path: str | Path,
) -> Path:
    """Exporta identidad y contactos en formato .pqcbackup cifrado y firmado."""
    registroDict = _serializarRegistro(registro)
    contactosLista = _serializarContactos(contactos)

    payloadPlano = {
        "registro": registroDict,
        "contactos": contactosLista,
    }
    payloadBytes = json.dumps(payloadPlano, ensure_ascii=True, separators=(",", ":")).encode(
        "utf-8"
    )

    salt = os.urandom(32)
    nonce = os.urandom(12)
    clave = _derivarClaveBackup(contrasenaBackup, salt)

    cifradoCompleto = AESGCM(clave).encrypt(nonce, payloadBytes, AAD_BACKUP)
    payloadCifrado = nonce + cifradoCompleto

    checksum = hashlib.blake2b(payloadCifrado, digest_size=32).digest()

    clavePrivadaB64 = str(registroDict["privkeyDilithiumB64"])
    clavePrivada = base64.b64decode(clavePrivadaB64)
    firmaChecksum = firmar(checksum, clavePrivada)

    kdfParams = {
        "algoritmo": "argon2id",
        "time_cost": 3,
        "memory_cost": 65536,
        "parallelism": 4,
        "salt_b64": base64.b64encode(salt).decode("ascii"),
    }
    kdfJson = json.dumps(kdfParams, ensure_ascii=True, separators=(",", ":")).encode("utf-8")

    if len(kdfJson) > 65535:
        raise ValueError("kdf_params excede el limite de longitud de 2 bytes.")
    if len(firmaChecksum) > 65535:
        raise ValueError("Firma excede el limite de longitud de 2 bytes.")

    destino = Path(path)
    destino.parent.mkdir(parents=True, exist_ok=True)

    contenido = bytearray()
    contenido += MAGIC_BACKUP
    contenido += struct.pack("<B", VERSION_BACKUP)
    contenido += struct.pack("<H", len(kdfJson))
    contenido += kdfJson
    contenido += struct.pack("<H", len(firmaChecksum))
    contenido += payloadCifrado
    contenido += checksum
    contenido += firmaChecksum

    destino.write_bytes(bytes(contenido))
    return destino
