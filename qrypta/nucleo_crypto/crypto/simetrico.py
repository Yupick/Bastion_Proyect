"""Cifrado simetrico.

Proposito: AES-256-GCM y derivacion de claves.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: cifrarAesGcm(datos, clave)
"""

from __future__ import annotations

import os

from .keygen import DependenciaCriptograficaError

try:
	from cryptography.hazmat.primitives import hashes
	from cryptography.hazmat.primitives.ciphers.aead import AESGCM
	from cryptography.hazmat.primitives.kdf.hkdf import HKDF
except ImportError:  # pragma: no cover - depende del entorno.
	AESGCM = None
	HKDF = None
	hashes = None


def _requiereCryptography() -> None:
	if AESGCM is None or HKDF is None or hashes is None:
		raise DependenciaCriptograficaError(
			"cryptography no esta disponible. Instala el paquete 'cryptography'."
		)


def derivarClave(secreto: bytes, contexto: bytes, salt: bytes | None = None) -> bytes:
	"""Deriva una clave de 256 bits con HKDF-SHA3-256."""
	_requiereCryptography()
	instanciaHkdf = HKDF(
		algorithm=hashes.SHA3_256(),
		length=32,
		salt=salt,
		info=contexto,
	)
	return instanciaHkdf.derive(secreto)


def cifrarAesGcm(datos: bytes, clave: bytes, aad: bytes = b"") -> tuple[bytes, bytes, bytes]:
	"""Cifra datos con AES-256-GCM y devuelve nonce, cifrado y tag."""
	_requiereCryptography()
	if len(clave) != 32:
		raise ValueError("La clave AES-256 debe tener exactamente 32 bytes.")

	nonce = os.urandom(12)
	cifradoCompleto = AESGCM(clave).encrypt(nonce, datos, aad)
	return nonce, cifradoCompleto[:-16], cifradoCompleto[-16:]


def descifrarAesGcm(
	nonce: bytes,
	cifrado: bytes,
	tag: bytes,
	clave: bytes,
	aad: bytes = b"",
) -> bytes:
	"""Descifra datos AES-256-GCM validando autenticidad."""
	_requiereCryptography()
	if len(clave) != 32:
		raise ValueError("La clave AES-256 debe tener exactamente 32 bytes.")
	return AESGCM(clave).decrypt(nonce, cifrado + tag, aad)
