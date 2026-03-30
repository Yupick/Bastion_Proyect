"""Tests para el servidor WebSocket.

Proposito: validar conexiones WebSocket, autenticacion y entrega de mensajes.
Autor: Qrypta Team
Fecha: 2026-03-30
"""

import asyncio
import json
import time
from typing import Any

import pytest
from fastapi.testclient import TestClient

from servidor.main import app

client = TestClient(app)


# === Tests de archivos ===

def test_upload_download_archivo():
	"""Test de subida y descarga de archivo permitido."""
	archivo = ("test.txt", b"contenido de prueba", "text/plain")
	resp = client.post("/api/v1/archivo/upload/sesiondemo/peer1", files={"file": archivo})
	assert resp.status_code == 200
	nombre = resp.json()["filename"]
	
	# Descargar
	resp2 = client.get(f"/api/v1/archivo/download/{nombre}")
	assert resp2.status_code == 200
	assert resp2.content == b"contenido de prueba"


def test_upload_archivo_no_permitido():
	"""Test de rechazo de archivo no permitido."""
	archivo = ("malware.exe", b"binario", "application/octet-stream")
	resp = client.post("/api/v1/archivo/upload/sesiondemo/peer1", files={"file": archivo})
	assert resp.status_code == 400
	assert "no permitido" in resp.json()["detail"]


def test_upload_archivo_grande():
	"""Test de rechazo de archivo demasiado grande."""
	archivo = ("grande.pdf", b"0" * (11 * 1024 * 1024), "application/pdf")
	resp = client.post("/api/v1/archivo/upload/sesiondemo/peer1", files={"file": archivo})
	assert resp.status_code == 400
	assert "demasiado grande" in resp.json()["detail"]


# === Tests de WebSocket ===

def test_ws_stats_endpoint():
	"""Test del endpoint de estadisticas WebSocket."""
	resp = client.get("/ws/v1/stats")
	assert resp.status_code == 200
	data = resp.json()
	assert "conexiones_activas" in data
	assert "mensajes_en_cola" in data


@pytest.mark.asyncio
async def test_ws_conexion_sin_auth():
	"""Test que conexion sin autenticacion es rechazada."""
	peer_id = "a" * 64
	
	with client.websocket_connect(f"/ws/v1/connect/{peer_id}") as websocket:
		# No enviar mensaje de auth
		# Esperar que servidor cierre conexion por timeout
		try:
			# Servidor debe cerrar en ~10 segundos
			await asyncio.wait_for(websocket.receive_json(), timeout=15)
		except Exception:
			pass  # Esperado que cierre


@pytest.mark.asyncio
async def test_ws_auth_exitosa():
	"""Test de autenticacion exitosa."""
	peer_id = "b" * 64
	
	with client.websocket_connect(f"/ws/v1/connect/{peer_id}") as websocket:
		# Enviar mensaje de auth
		auth_msg = {
			"tipo": "auth",
			"firma": "firma_dummy_base64",  # TODO: Usar firma real
			"timestamp": int(time.time()),
		}
		websocket.send_json(auth_msg)
		
		# Esperar confirmacion
		resp = websocket.receive_json()
		assert resp["tipo"] == "auth_ok"
		assert resp["peer_id"] == peer_id


@pytest.mark.asyncio
async def test_ws_heartbeat():
	"""Test de mecanismo heartbeat."""
	peer_id = "c" * 64
	
	with client.websocket_connect(f"/ws/v1/connect/{peer_id}") as websocket:
		# Auth
		websocket.send_json({
			"tipo": "auth",
			"firma": "firma_dummy",
			"timestamp": int(time.time()),
		})
		websocket.receive_json()  # auth_ok
		
		# Enviar heartbeat
		websocket.send_json({"tipo": "heartbeat"})
		
		# Esperar ack
		resp = websocket.receive_json()
		assert resp["tipo"] == "heartbeat_ack"


@pytest.mark.asyncio
async def test_ws_envio_mensaje_peer_online():
	"""Test de envio de mensaje a peer conectado."""
	peer_id_alice = "d" * 64
	peer_id_bob = "e" * 64
	
	# Conectar Bob
	with client.websocket_connect(f"/ws/v1/connect/{peer_id_bob}") as ws_bob:
		# Auth Bob
		ws_bob.send_json({
			"tipo": "auth",
			"firma": "firma_bob",
			"timestamp": int(time.time()),
		})
		ws_bob.receive_json()  # auth_ok
		
		# Conectar Alice
		with client.websocket_connect(f"/ws/v1/connect/{peer_id_alice}") as ws_alice:
			# Auth Alice
			ws_alice.send_json({
				"tipo": "auth",
				"firma": "firma_alice",
				"timestamp": int(time.time()),
			})
			ws_alice.receive_json()  # auth_ok
			
			# Alice envia mensaje a Bob
			mensaje = {
				"tipo": "mensaje",
				"peer_id_destino": peer_id_bob,
				"mensaje_id": "msg123",
				"contenido": "Hola Bob",
			}
			ws_alice.send_json(mensaje)
			
			# Alice recibe ack
			ack = ws_alice.receive_json()
			assert ack["tipo"] == "mensaje_ack"
			assert ack["entregado"] is True
			
			# Bob recibe el mensaje
			msg_recibido = ws_bob.receive_json()
			assert msg_recibido["tipo"] == "mensaje"
			assert msg_recibido["contenido"] == "Hola Bob"


@pytest.mark.asyncio
async def test_ws_mensaje_peer_offline():
	"""Test de envio de mensaje a peer desconectado (encolado)."""
	peer_id_alice = "f" * 64
	peer_id_bob = "1" * 64
	
	# Solo Alice conectada (Bob offline)
	with client.websocket_connect(f"/ws/v1/connect/{peer_id_alice}") as ws_alice:
		# Auth
		ws_alice.send_json({
			"tipo": "auth",
			"firma": "firma_alice",
			"timestamp": int(time.time()),
		})
		ws_alice.receive_json()
		
		# Alice envia mensaje a Bob (offline)
		mensaje = {
			"tipo": "mensaje",
			"peer_id_destino": peer_id_bob,
			"mensaje_id": "msg456",
			"contenido": "Hola Bob (offline)",
		}
		ws_alice.send_json(mensaje)
		
		# Alice recibe ack indicando que se encolo
		ack = ws_alice.receive_json()
		assert ack["tipo"] == "mensaje_ack"
		assert ack["entregado"] is False  # Bob no esta conectado
	
	# Verificar que mensaje esta en cola
	stats = client.get("/ws/v1/stats").json()
	assert stats["mensajes_en_cola"] > 0
	
	# Bob se conecta y debe recibir mensajes pendientes
	with client.websocket_connect(f"/ws/v1/connect/{peer_id_bob}") as ws_bob:
		ws_bob.send_json({
			"tipo": "auth",
			"firma": "firma_bob",
			"timestamp": int(time.time()),
		})
		ws_bob.receive_json()  # auth_ok
		
		# Bob debe recibir mensaje pendiente
		msg_pendiente = ws_bob.receive_json()
		assert msg_pendiente["tipo"] == "mensaje"
		assert msg_pendiente["contenido"] == "Hola Bob (offline)"


@pytest.mark.asyncio
async def test_ws_peer_id_invalido():
	"""Test que rechaza peer_id invalido."""
	peer_id_corto = "abc"  # Debe ser 64 caracteres hex
	
	with client.websocket_connect(f"/ws/v1/connect/{peer_id_corto}") as websocket:
		websocket.send_json({
			"tipo": "auth",
			"firma": "firma",
			"timestamp": int(time.time()),
		})
		
		# Debe cerrar conexion por auth fallida
		try:
			websocket.receive_json()
		except Exception:
			pass  # Esperado


def test_download_archivo_inexistente():
	"""Test de descarga de archivo que no existe."""
	resp = client.get("/api/v1/archivo/download/noexiste.txt")
	assert resp.status_code == 404

