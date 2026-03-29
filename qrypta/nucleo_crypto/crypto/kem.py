"""Kyber KEM.

Proposito: encapsular y desencapsular secretos compartidos.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: encapsular(pubkey)
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


def encapsular(clavePublicaKyber: bytes) -> tuple[bytes, bytes]:
	"""Encapsula un secreto para una clave publica Kyber768.

	Devuelve: (textoCifrado, secretoCompartido)
	"""
	_requiereLiboqs()
	with oqs.KeyEncapsulation("Kyber768") as clienteKem:
		resultado = clienteKem.encap_secret(clavePublicaKyber)

	if len(resultado) != 2:
		raise RuntimeError("Resultado inesperado al encapsular secreto.")

	primerValor, segundoValor = resultado
	if len(primerValor) > len(segundoValor):
		return primerValor, segundoValor
	return segundoValor, primerValor


def desencapsular(clavePrivadaKyber: bytes, textoCifrado: bytes) -> bytes:
	"""Desencapsula un secreto compartido usando clave privada Kyber768."""
	_requiereLiboqs()
	with oqs.KeyEncapsulation("Kyber768", secret_key=clavePrivadaKyber) as clienteKem:
		secretoCompartido = clienteKem.decap_secret(textoCifrado)
	return secretoCompartido
