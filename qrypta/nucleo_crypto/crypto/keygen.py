"""Generacion de claves PQC.

Proposito: generar pares Kyber y Dilithium.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: generarParKyber()
"""

from __future__ import annotations

try:
	import oqs
except ImportError:  # pragma: no cover - depende del entorno.
	oqs = None


class DependenciaCriptograficaError(RuntimeError):
	"""Error cuando una dependencia criptografica no esta disponible."""


def _requiereLiboqs() -> None:
	if oqs is None:
		raise DependenciaCriptograficaError(
			"liboqs-python no esta disponible. Instala el paquete 'oqs'."
		)


def generarParKyber() -> tuple[bytes, bytes]:
	"""Genera un par de claves Kyber768 (publica, privada)."""
	_requiereLiboqs()
	with oqs.KeyEncapsulation("Kyber768") as clienteKem:
		clavePublica = clienteKem.generate_keypair()
		clavePrivada = clienteKem.export_secret_key()
	return clavePublica, clavePrivada


def generarParDilithium() -> tuple[bytes, bytes]:
	"""Genera un par de claves Dilithium3 (publica, privada)."""
	_requiereLiboqs()
	with oqs.Signature("Dilithium3") as clienteFirma:
		clavePublica = clienteFirma.generate_keypair()
		clavePrivada = clienteFirma.export_secret_key()
	return clavePublica, clavePrivada
