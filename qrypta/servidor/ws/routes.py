"""Rutas WebSocket para conexiones en tiempo real.

Proposito: manejar conexiones WebSocket autenticadas con entrega de mensajes en tiempo real.
Autor: Qrypta Team
Fecha: 2026-03-30
"""

from __future__ import annotations

import asyncio
import base64
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from servidor.auditoria.logger import auditor

from .archivos import ArchivoInvalido, validar_archivo
from .sesiones import GestorSesiones

router = APIRouter()
gestor = GestorSesiones()

# Estructura: {peer_id: websocket}
_conexionesActivas: dict[str, WebSocket] = {}

# Estructura: {peer_id: ultimo_heartbeat_timestamp}
_ultimoHeartbeat: dict[str, float] = {}

# Persistencia de mensajes pendientes (DB)
from servidor.persistencia.mensajes import (
    MensajePendiente, guardar_mensaje, obtener_mensajes, eliminar_mensajes, limpiar_expirados, init_db
)

# _colaMensajes: dict[str, list[dict[str, Any]]] = defaultdict(list)

UPLOAD_DIR = Path(__file__).parent.parent / "archivos_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Constantes
HEARTBEAT_INTERVALO = 30  # segundos
HEARTBEAT_TIMEOUT = 90  # segundos
MAX_MENSAJES_COLA = 100


class ErrorAutenticacion(Exception):
	"""Error de autenticacion WebSocket."""


async def _verificar_autenticacion(peer_id: str, firma_b64: str, timestamp: int) -> bool:
	"""Verifica la firma de autenticacion del cliente.
	
	Args:
		peer_id: ID del peer (hex)
		firma_b64: Firma Dilithium en base64
		timestamp: Timestamp del mensaje de autenticacion
	
	Returns:
		True si la firma es valida
	
	Nota:
		Por ahora acepta cualquier peer_id valido.
		En produccion, verificar firma con clave publica del peer.
	"""
	# TODO: Implementar verificacion real de firma Dilithium
	# 1. Obtener clave publica Dilithium del peer_id (desde DB o DHT)
	# 2. Verificar firma del payload: peer_id + timestamp
	# 3. Verificar que timestamp no sea muy antiguo (replay protection)
	
	# Validacion basica por ahora
	if not peer_id or len(peer_id) != 64:  # 32 bytes en hex
		return False
	
	if not firma_b64:
		return False
	
	# Verificar que timestamp no sea muy antiguo (max 5 minutos)
	ahora = int(time.time())
	if abs(ahora - timestamp) > 300:
		return False
	
	return True


async def _enviar_mensaje_tiempo_real(peer_id_destino: str, mensaje: dict[str, Any]) -> bool:
	"""Intenta enviar mensaje en tiempo real si el peer esta conectado.
	
	Args:
		peer_id_destino: ID del peer destino
		mensaje: Mensaje a enviar
	
	Returns:
		True si se envio exitosamente, False si el peer no esta conectado
	"""
	websocket = _conexionesActivas.get(peer_id_destino)
	
	if websocket is None:
		return False
	
	try:
		await websocket.send_json(mensaje)
		auditor.registrarEvento("ws_mensaje_entregado", len(json.dumps(mensaje)), True)
		return True
	except Exception as e:
		# Conexion cerrada o error
		auditor.registrarEvento("ws_mensaje_error", 0, False)
		# Limpiar conexion muerta
		_conexionesActivas.pop(peer_id_destino, None)
		_ultimoHeartbeat.pop(peer_id_destino, None)
		return False


async def _encolar_mensaje(peer_id_destino: str, mensaje: dict[str, Any]) -> None:
    """Encola mensaje para entrega posterior cuando el peer se conecte (persistente)."""
    # Limitar tamaño de mensajes por peer
    mensajes = obtener_mensajes(peer_id_destino)
    if len(mensajes) >= MAX_MENSAJES_COLA:
        # Eliminar el más antiguo
        eliminar_mensajes(peer_id_destino)
    # Guardar mensaje
    guardar_mensaje(MensajePendiente(peer_id_destino, json.dumps(mensaje), time.time()))
    auditor.registrarEvento("ws_mensaje_encolado", len(json.dumps(mensaje)), True)


async def _entregar_mensajes_pendientes(peer_id: str, websocket: WebSocket) -> None:
    """Entrega mensajes pendientes a un peer recien conectado (desde DB)."""
    mensajes = obtener_mensajes(peer_id)
    if not mensajes:
        return
    for mensaje in mensajes:
        try:
            await websocket.send_json(json.loads(mensaje.payload))
        except Exception:
            # Si falla, dejar mensajes en DB
            break
    else:
        # Todos entregados exitosamente
        eliminar_mensajes(peer_id)
        auditor.registrarEvento("ws_mensajes_pendientes_entregados", len(mensajes), True)


async def _heartbeat_monitor() -> None:
	"""Monitorea conexiones y cierra las que no responden heartbeat."""
	while True:
		await asyncio.sleep(HEARTBEAT_INTERVALO)
		
		ahora = time.time()
		peers_inactivos = []
		
		for peer_id, ultimo_hb in _ultimoHeartbeat.items():
			if ahora - ultimo_hb > HEARTBEAT_TIMEOUT:
				peers_inactivos.append(peer_id)
		
		for peer_id in peers_inactivos:
			websocket = _conexionesActivas.get(peer_id)
			if websocket:
				try:
					await websocket.close(code=1000, reason="Heartbeat timeout")
				except Exception:
					pass
			
			_conexionesActivas.pop(peer_id, None)
			_ultimoHeartbeat.pop(peer_id, None)
			auditor.registrarEvento("ws_timeout", 0, True)


@router.on_event("startup")
async def startup_event() -> None:
    """Inicia monitor de heartbeat y base de datos."""
    init_db()
    asyncio.create_task(_heartbeat_monitor())


@router.websocket("/ws/v1/connect/{peer_id}")
async def ws_connect(websocket: WebSocket, peer_id: str) -> None:
	"""Endpoint de conexion WebSocket autenticada.
	
	Flujo:
	1. Cliente se conecta con peer_id
	2. Cliente envia mensaje de autenticacion con firma
	3. Servidor verifica firma
	4. Si valida, mantiene conexion abierta
	5. Entrega mensajes pendientes
	6. Escucha mensajes del cliente y heartbeats
	
	Args:
		websocket: Conexion WebSocket
		peer_id: ID del peer (hex, 64 caracteres)
	"""
	await websocket.accept()
	
	try:
		# Esperar mensaje de autenticacion (timeout 10s)
		try:
			auth_data = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
		except asyncio.TimeoutError:
			await websocket.close(code=1008, reason="Auth timeout")
			return
		
		# Verificar autenticacion
		if auth_data.get("tipo") != "auth":
			await websocket.close(code=1008, reason="Auth required")
			return
		
		firma_b64 = auth_data.get("firma")
		timestamp = auth_data.get("timestamp")
		
		if not await _verificar_autenticacion(peer_id, firma_b64, timestamp):
			await websocket.close(code=1008, reason="Auth failed")
			auditor.registrarEvento("ws_auth_fallida", 0, False)
			return
		
		# Autenticacion exitosa
		_conexionesActivas[peer_id] = websocket
		_ultimoHeartbeat[peer_id] = time.time()
		auditor.registrarEvento("ws_conectado", 0, True)
		
		# Enviar confirmacion
		await websocket.send_json({
			"tipo": "auth_ok",
			"peer_id": peer_id,
			"timestamp": int(time.time()),
		})
		
		# Entregar mensajes pendientes
		await _entregar_mensajes_pendientes(peer_id, websocket)
		
		# Loop principal: recibir mensajes
		while True:
			data = await websocket.receive_json()
			tipo = data.get("tipo")
			
			if tipo == "heartbeat":
				_ultimoHeartbeat[peer_id] = time.time()
				await websocket.send_json({"tipo": "heartbeat_ack"})
			
			elif tipo == "mensaje":
				# Mensaje para otro peer
				peer_id_destino = data.get("peer_id_destino")
				if not peer_id_destino:
					continue
				
				# Intentar entrega en tiempo real
				enviado = await _enviar_mensaje_tiempo_real(peer_id_destino, data)
				
				if not enviado:
					# Encolar para entrega posterior
					await _encolar_mensaje(peer_id_destino, data)
				
				# Confirmar al emisor
				await websocket.send_json({
					"tipo": "mensaje_ack",
					"mensaje_id": data.get("mensaje_id"),
					"entregado": enviado,
				})
	
	except WebSocketDisconnect:
		pass
	except Exception as e:
		auditor.registrarEvento("ws_error", 0, False)
	finally:
		# Limpiar conexion
		_conexionesActivas.pop(peer_id, None)
		_ultimoHeartbeat.pop(peer_id, None)
		auditor.registrarEvento("ws_desconectado", 0, True)


@router.get("/ws/v1/stats")
async def ws_stats() -> dict[str, Any]:
    """Devuelve estadisticas de conexiones WebSocket y mensajes pendientes."""
    # Contar mensajes pendientes en DB
    import sqlite3
    conn = sqlite3.connect("servidor_mensajes.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*), COUNT(DISTINCT peer_id) FROM mensajes_pendientes")
    total, peers = c.fetchone()
    conn.close()
    return {
        "conexiones_activas": len(_conexionesActivas),
        "peers_conectados": list(_conexionesActivas.keys()),
        "mensajes_en_cola": total,
        "peers_con_mensajes_pendientes": peers,
    }


# === Endpoints de archivos ===

@router.post("/api/v1/archivo/upload/{sesion_id}/{peer_id}")
async def upload_archivo(sesion_id: str, peer_id: str, file: UploadFile = File(...)) -> dict[str, Any]:
	"""Sube un archivo cifrado."""
	try:
		validar_archivo(file.filename, file.spool_max_size or 0)
	except ArchivoInvalido as e:
		raise HTTPException(status_code=400, detail=str(e))
	
	ext = Path(file.filename).suffix
	nombre = f"{uuid4().hex}{ext}"
	ruta = UPLOAD_DIR / nombre
	
	with open(ruta, "wb") as f:
		contenido = await file.read()
		f.write(contenido)
	
	auditor.registrarEvento("archivo_subido", len(contenido), True)
	return {"ok": True, "filename": nombre, "size": len(contenido)}


@router.get("/api/v1/archivo/download/{filename}")
async def download_archivo(filename: str) -> FileResponse:
	"""Descarga un archivo cifrado."""
	ruta = UPLOAD_DIR / filename
	if not ruta.exists():
		raise HTTPException(status_code=404, detail="Archivo no encontrado")
	
	auditor.registrarEvento("archivo_descargado", ruta.stat().st_size, True)
	return FileResponse(ruta, filename=filename)
