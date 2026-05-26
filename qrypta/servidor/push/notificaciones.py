"""Relay de notificaciones push.

Proposito: avisar mensajes pendientes sin exponer contenido.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: enviar aviso FCM/APNs
"""

from __future__ import annotations

from typing import Final

TIPO_AVISO_MENSAJE_PENDIENTE: Final[str] = "mensaje_pendiente"


def construir_payload_aviso(peer_id: str, tipo_aviso: str = TIPO_AVISO_MENSAJE_PENDIENTE) -> dict[str, str]:
	"""Construye payload minimo de push sin contenido sensible."""
	return {
		"peer_id": peer_id,
		"tipo": tipo_aviso,
	}


def enviar_a_proveedor(token_push: str, payload: dict[str, str]) -> bool:
	"""Simula envio a proveedor (FCM/APNs).

	En esta fase solo validamos contrato y devolvemos exito.
	"""
	_ = token_push
	_ = payload
	return True
