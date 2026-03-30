"""Rutas API.

Proposito: exponer endpoints REST.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: incluir router en main.py
"""

from __future__ import annotations

from collections import deque
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Request

# Importar y montar el router de DHT
from .dht_api import router as dht_router
from .push_api import router as push_router
from .grupos_api import router as grupos_router

from servidor.api.modelos import MensajeEntrada, MensajeSalida, RespuestaEstado, RespuestaOk
from servidor.auditoria.logger import auditor
from servidor.config.settings import settings

router = APIRouter()
router.include_router(dht_router)
router.include_router(push_router)
router.include_router(grupos_router)

_mensajesPendientes: dict[str, deque[MensajeSalida]] = {}
_historialRequestsPorIp: dict[str, deque[datetime]] = {}
_inicioServidor = datetime.now(UTC)


def _expirado(mensaje: MensajeSalida) -> bool:
	limite = datetime.now(UTC) - timedelta(hours=settings.ttlMensajesHoras)
	return mensaje.timestamp < limite


def limpiarMensajesExpirados() -> None:
	"""Elimina mensajes vencidos según TTL configurado."""
	peersVacios: list[str] = []
	for peerId, cola in _mensajesPendientes.items():
		vigentes = deque((item for item in cola if not _expirado(item)), maxlen=settings.maxMensajesPorPeer)
		_mensajesPendientes[peerId] = vigentes
		if not vigentes:
			peersVacios.append(peerId)

	for peerId in peersVacios:
		_mensajesPendientes.pop(peerId, None)


def contarMensajesPendientes() -> int:
	"""Devuelve el total agregado de mensajes en cola."""
	return sum(len(cola) for cola in _mensajesPendientes.values())


def resetearAlmacenMensajes() -> None:
	"""Reinicia almacenamiento en memoria (uso en tests)."""
	_mensajesPendientes.clear()
	_historialRequestsPorIp.clear()


def _limiteRequestsPorMinuto() -> int:
	valor = settings.rateLimit.strip().split("/")[0]
	try:
		return max(1, int(valor))
	except ValueError:
		return 30


def _verificarRateLimit(request: Request) -> None:
	limite = _limiteRequestsPorMinuto()
	ahora = datetime.now(UTC)
	ventana = ahora - timedelta(minutes=1)
	ip = request.client.host if request.client else "desconocido"

	historial = _historialRequestsPorIp.setdefault(ip, deque())
	while historial and historial[0] < ventana:
		historial.popleft()

	if len(historial) >= limite:
		raise HTTPException(status_code=429, detail="Rate limit excedido")

	historial.append(ahora)


@router.post("/v1/mensaje", response_model=RespuestaOk)
async def enviarMensaje(request: Request, entrada: MensajeEntrada) -> RespuestaOk:
	"""Encola un mensaje cifrado para un peer destino."""
	_verificarRateLimit(request)
	limpiarMensajesExpirados()

	cola = _mensajesPendientes.setdefault(
		entrada.peerIdDestino,
		deque(maxlen=settings.maxMensajesPorPeer),
	)

	mensaje = MensajeSalida(
		id=uuid4(),
		peerIdOrigen=entrada.peerIdOrigen,
		payloadCifradoB64=entrada.payloadCifradoB64,
		timestamp=entrada.timestamp,
		firmaB64=entrada.firmaB64,
	)
	cola.append(mensaje)
	auditor.registrarEvento("mensaje_recibido", len(entrada.payloadCifradoB64), True)
	return RespuestaOk(ok=True, mensaje="Mensaje encolado")


@router.get("/v1/mensajes/{peerId}", response_model=list[MensajeSalida])
async def obtenerMensajes(request: Request, peerId: str) -> list[MensajeSalida]:
	"""Devuelve y elimina mensajes pendientes de un peer."""
	_verificarRateLimit(request)
	limpiarMensajesExpirados()
	cola = _mensajesPendientes.get(peerId)
	if not cola:
		auditor.registrarEvento("mensajes_consulta", 0, True)
		return []

	mensajes = list(cola)
	_mensajesPendientes.pop(peerId, None)
	auditor.registrarEvento("mensajes_entregados", len(mensajes), True)
	return mensajes


@router.get("/v1/estado", response_model=RespuestaEstado)
async def obtenerEstado(request: Request) -> RespuestaEstado:
	"""Devuelve salud y métricas agregadas del servidor."""
	_ = request
	limpiarMensajesExpirados()
	ahora = datetime.now(UTC)
	uptime = int((ahora - _inicioServidor).total_seconds())
	return RespuestaEstado(
		version="0.1.0",
		timestamp=ahora,
		mensajesPendientes=contarMensajesPendientes(),
		uptimeS=uptime,
	)


@router.delete("/v1/admin/mensajes", response_model=RespuestaOk)
async def limpiarMensajesAdmin(
	request: Request,
	xAdminToken: str | None = Header(default=None, alias="X-Admin-Token"),
) -> RespuestaOk:
	"""Limpia cola de mensajes con token administrativo."""
	_ = request
	if xAdminToken != settings.adminToken:
		auditor.registrarEvento("admin_limpiar_mensajes", 0, False)
		raise HTTPException(status_code=401, detail="Token de administrador invalido")

	_mensajesPendientes.clear()
	auditor.registrarEvento("admin_limpiar_mensajes", 0, True)
	return RespuestaOk(ok=True, mensaje="Mensajes pendientes eliminados")
