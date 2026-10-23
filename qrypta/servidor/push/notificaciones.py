"""Relay de notificaciones push.

Proposito: avisar mensajes pendientes sin exponer contenido.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: enviar aviso FCM/APNs
"""

from __future__ import annotations

import os
from typing import Final

import httpx

TIPO_AVISO_MENSAJE_PENDIENTE: Final[str] = "mensaje_pendiente"

# Configuracion de proveedores
FCM_URL: Final[str] = "https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
APNS_URL_SANDBOX: Final[str] = "https://api.sandbox.push.apple.com"
APNS_URL_PROD: Final[str] = "https://api.push.apple.com"

# Modo stub: si True, no envia realmente (para tests sin credenciales)
_STUB_MODE = os.getenv("QRYPTA_PUSH_STUB", "true").lower() == "true"

# Configuracion FCM
_FCM_PROJECT_ID = os.getenv("FCM_PROJECT_ID", "")
_FCM_CREDENTIALS_PATH = os.getenv("FCM_CREDENTIALS_PATH", "")

# Configuracion APNs
_APNS_KEY_ID = os.getenv("APNS_KEY_ID", "")
_APNS_TEAM_ID = os.getenv("APNS_TEAM_ID", "")
_APNS_BUNDLE_ID = os.getenv("APNS_BUNDLE_ID", "")
_APNS_AUTH_KEY_PATH = os.getenv("APNS_AUTH_KEY_PATH", "")
_APNS_USE_SANDBOX = os.getenv("APNS_USE_SANDBOX", "true").lower() == "true"


def _stub_mode() -> bool:
	"""Verifica si estamos en modo stub."""
	return _STUB_MODE


def construir_payload_aviso(peer_id: str, tipo_aviso: str = TIPO_AVISO_MENSAJE_PENDIENTE) -> dict[str, str]:
	"""Construye payload minimo de push sin contenido sensible."""
	return {
		"peer_id": peer_id,
		"tipo": tipo_aviso,
	}


def _construir_fcm_message(token: str, payload: dict[str, str]) -> dict:
	"""Construye mensaje en formato FCM HTTP v1."""
	return {
		"message": {
			"token": token,
			"data": payload,
			"android": {
				"priority": "high",
			},
			"apns": {
				"headers": {
					"apns-priority": "10",
				},
			},
		}
	}


async def _enviar_fcm(token_push: str, payload: dict[str, str]) -> bool:
	"""Envia notificacion via FCM HTTP v1 API."""
	if not _FCM_PROJECT_ID or not _FCM_CREDENTIALS_PATH:
		return False

	try:
		# En produccion, usar google-auth para obtener access token
		# Por ahora, requerir FCM_ACCESS_TOKEN en env
		access_token = os.getenv("FCM_ACCESS_TOKEN")
		if not access_token:
			return False

		url = FCM_URL.format(project_id=_FCM_PROJECT_ID)
		message = _construir_fcm_message(token_push, payload)

		async with httpx.AsyncClient(timeout=10.0) as client:
			resp = await client.post(
				url,
				json=message,
				headers={
					"Authorization": f"Bearer {access_token}",
					"Content-Type": "application/json",
				},
			)
			return resp.status_code == 200
	except Exception:
		return False


def _construir_apns_payload(payload: dict[str, str]) -> bytes:
	"""Construye payload APNs en formato JSON."""
	import json
	apns_payload = {
		"aps": {
			"content-available": 1,
			"priority": 10,
		},
		"custom": payload,
	}
	return json.dumps(apns_payload, separators=(",", ":")).encode("utf-8")


async def _enviar_apns(token_push: str, payload: dict[str, str]) -> bool:
	"""Envia notificacion via APNs (requiere HTTP/2 y JWT auth)."""
	if not all([_APNS_KEY_ID, _APNS_TEAM_ID, _APNS_BUNDLE_ID, _APNS_AUTH_KEY_PATH]):
		return False

	try:
		# En produccion, generar JWT con auth key
		# Por ahora, requerir APNS_AUTH_TOKEN en env
		auth_token = os.getenv("APNS_AUTH_TOKEN")
		if not auth_token:
			return False

		url_base = APNS_URL_SANDBOX if _APNS_USE_SANDBOX else APNS_URL_PROD
		url = f"{url_base}/3/device/{token_push}"

		apns_payload = _construir_apns_payload(payload)

		async with httpx.AsyncClient(timeout=10.0, http2=True) as client:
			resp = await client.post(
				url,
				content=apns_payload,
				headers={
					"authorization": f"bearer {auth_token}",
					"apns-topic": _APNS_BUNDLE_ID,
					"apns-priority": "10",
					"content-type": "application/json",
				},
			)
			return resp.status_code == 200
	except Exception:
		return False


async def enviar_a_proveedor(token_push: str, payload: dict[str, str]) -> bool:
	"""Envia notificacion al proveedor correspondiente (FCM o APNs).

	En modo stub (default), solo valida contrato y devuelve exito.
	En modo produccion, requiere credenciales configuradas via variables de entorno.
	"""
	if _stub_mode():
		_ = token_push
		_ = payload
		return True

	# Detectar proveedor por formato de token (heuristico)
	# FCM tokens suelen ser mas largos y alfanumericos
	# APNs tokens son 64 chars hex
	if len(token_push) == 64 and all(c in "0123456789abcdef" for c in token_push.lower()):
		return await _enviar_apns(token_push, payload)
	else:
		return await _enviar_fcm(token_push, payload)