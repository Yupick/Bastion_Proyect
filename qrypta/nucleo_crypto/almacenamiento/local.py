"""Persistencia local cifrada.

Proposito: guardar datos del usuario sin base central.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: guardarIdentidad(...)
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from nucleo_crypto.crypto.keygen import DependenciaCriptograficaError

try:
    from argon2.low_level import Type, hash_secret_raw
except ImportError:  # pragma: no cover - depende del entorno.
    Type = None
    hash_secret_raw = None

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:  # pragma: no cover - depende del entorno.
    AESGCM = None

VERSION_FORMATO = 1
NOMBRE_ARCHIVO_IDENTIDAD = "identidad.enc"


def _requiereDependencias() -> None:
    if hash_secret_raw is None or Type is None:
        raise DependenciaCriptograficaError(
            "La dependencia 'argon2-cffi' no esta disponible. Instala 'argon2-cffi'."
        )
    if AESGCM is None:
        raise DependenciaCriptograficaError(
            "La dependencia 'cryptography' no esta disponible. Instala 'cryptography'."
        )


def obtenerDirectorioBase() -> Path:
    """Devuelve el directorio base local de Qrypta."""
    return Path.home() / ".qrypta"


def derivarClaveMaestra(contrasena: str, salt: bytes) -> bytes:
    """Deriva clave maestra con Argon2id."""
    _requiereDependencias()
    return hash_secret_raw(
        secret=contrasena.encode("utf-8"),
        salt=salt,
        time_cost=2,
        memory_cost=102400,
        parallelism=4,
        hash_len=32,
        type=Type.ID,
    )


def guardarIdentidad(datos: dict[str, Any], contrasena: str, ruta: Path | None = None) -> Path:
    """Guarda identidad en formato cifrado .enc."""
    destino = ruta or (obtenerDirectorioBase() / NOMBRE_ARCHIVO_IDENTIDAD)
    destino.parent.mkdir(parents=True, exist_ok=True)

    salt = os.urandom(16)
    nonce = os.urandom(12)
    clave = derivarClaveMaestra(contrasena, salt)

    payload = json.dumps(datos, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    cifradoCompleto = AESGCM(clave).encrypt(nonce, payload, b"qrypta-identidad-v1")

    checksum = hashlib.blake2b(cifradoCompleto, digest_size=32).digest()
    estructura = {
        "version": VERSION_FORMATO,
        "kdf_params": {
            "algoritmo": "argon2id",
            "time_cost": 2,
            "memory_cost": 102400,
            "parallelism": 4,
            "salt_b64": base64.b64encode(salt).decode("ascii"),
        },
        "nonce_b64": base64.b64encode(nonce).decode("ascii"),
        "cifrado_b64": base64.b64encode(cifradoCompleto).decode("ascii"),
        "checksum_b64": base64.b64encode(checksum).decode("ascii"),
    }
    destino.write_text(json.dumps(estructura, ensure_ascii=True, indent=2), encoding="utf-8")
    return destino


def cargarIdentidad(contrasena: str, ruta: Path | None = None) -> dict[str, Any]:
    """Carga identidad desde archivo cifrado .enc."""
    origen = ruta or (obtenerDirectorioBase() / NOMBRE_ARCHIVO_IDENTIDAD)
    estructura = json.loads(origen.read_text(encoding="utf-8"))

    salt = base64.b64decode(estructura["kdf_params"]["salt_b64"])
    nonce = base64.b64decode(estructura["nonce_b64"])
    cifrado = base64.b64decode(estructura["cifrado_b64"])
    checksum = base64.b64decode(estructura["checksum_b64"])

    if hashlib.blake2b(cifrado, digest_size=32).digest() != checksum:
        raise ValueError("El checksum del archivo cifrado no coincide.")

    clave = derivarClaveMaestra(contrasena, salt)
    plano = AESGCM(clave).decrypt(nonce, cifrado, b"qrypta-identidad-v1")
    return json.loads(plano.decode("utf-8"))
