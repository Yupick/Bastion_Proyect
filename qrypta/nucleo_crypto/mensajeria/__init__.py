"""Modulo de mensajeria E2E.

Proposito: cifrado y descifrado de mensajes entre peers.
"""

from .mensaje import (
	ErrorMensaje,
	ErrorVerificacion,
	MensajeCifrado,
	cifrar_para_contacto,
	descifrar_de_contacto,
)

__all__ = [
	"MensajeCifrado",
	"cifrar_para_contacto",
	"descifrar_de_contacto",
	"ErrorMensaje",
	"ErrorVerificacion",
]
