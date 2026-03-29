"""Recuperacion por mnemotecnica.

Proposito: soporte BIP-39 para recuperacion segura.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: generarMnemonic()
"""

from __future__ import annotations

from typing import Sequence

from nucleo_crypto.crypto.keygen import DependenciaCriptograficaError

try:
    from argon2.low_level import Type, hash_secret_raw
except ImportError:  # pragma: no cover - depende del entorno.
    Type = None
    hash_secret_raw = None

try:
    from mnemonic import Mnemonic
except ImportError:  # pragma: no cover - depende del entorno.
    Mnemonic = None


def _requiereDependencias() -> None:
    if Mnemonic is None:
        raise DependenciaCriptograficaError(
            "La dependencia 'mnemonic' no esta disponible. Instala 'mnemonic'."
        )
    if hash_secret_raw is None or Type is None:
        raise DependenciaCriptograficaError(
            "La dependencia 'argon2-cffi' no esta disponible. Instala 'argon2-cffi'."
        )


def generarMnemonic() -> tuple[bytes, list[str]]:
    """Genera entropia y una frase BIP-39 de 24 palabras."""
    _requiereDependencias()
    motorBip39 = Mnemonic("english")
    frase = motorBip39.generate(strength=256)
    palabras = frase.split()
    entropiaValor = motorBip39.to_entropy(frase)
    if isinstance(entropiaValor, (bytes, bytearray)):
        entropia = bytes(entropiaValor)
    else:
        entropia = bytes.fromhex(entropiaValor)
    return entropia, palabras


def recuperarDesde(palabras: Sequence[str]) -> bytes:
    """Recupera la entropia original a partir de palabras BIP-39."""
    _requiereDependencias()
    frase = " ".join(palabras).strip()
    motorBip39 = Mnemonic("english")
    if not motorBip39.check(frase):
        raise ValueError("La frase mnemotecnica no es valida.")
    entropiaValor = motorBip39.to_entropy(frase)
    if isinstance(entropiaValor, (bytes, bytearray)):
        return bytes(entropiaValor)
    return bytes.fromhex(entropiaValor)


def derivarClaveDesdeEntropia(entropia: bytes, salt: bytes | None = None) -> bytes:
    """Deriva una clave AES-256 desde entropia usando Argon2id."""
    _requiereDependencias()
    saltEfectivo = salt or b"qrypta-recuperacion-v1"
    return hash_secret_raw(
        secret=entropia,
        salt=saltEfectivo,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        type=Type.ID,
    )
