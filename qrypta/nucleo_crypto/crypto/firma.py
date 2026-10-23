"""Firma digital Dilithium.

Proposito: firmar y verificar mensajes.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: firmar(mensaje, clave)
"""

from __future__ import annotations

from .keygen import DependenciaCriptograficaError

try:
	import oqs
except ImportError:  # pragma: no cover - depende del entorno.
	oqs = None


def _requiereLiboqs() -> None:
	if oqs is None:
		raise DependenciaCriptograficaError(
			"liboqs-python no esta disponible. Instala el paquete 'oqs'."
		)


def firmar(mensaje: bytes, clavePrivadaDilithium: bytes) -> bytes:
	"""Firma un mensaje usando ML-DSA-65."""
	_requiereLiboqs()
	with oqs.Signature("ML-DSA-65", secret_key=clavePrivadaDilithium) as clienteFirma:
		firmaDigital = clienteFirma.sign(mensaje)
	return firmaDigital


def verificar(mensaje: bytes, firmaDigital: bytes, clavePublicaDilithium: bytes) -> bool:
	"""Verifica una firma ML-DSA-65."""
	_requiereLiboqs()
	with oqs.Signature("ML-DSA-65") as clienteFirma:
		return bool(clienteFirma.verify(mensaje, firmaDigital, clavePublicaDilithium))
