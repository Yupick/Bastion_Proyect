"""Nodo DHT.

Proposito: descubrimiento de pares sin base central.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: publicar/buscar peer_id
"""

import time
from typing import Optional, Dict

class NodoDHT:
	"""
	Nodo DHT simplificado para descubrimiento de peers.
	"""
	def __init__(self):
		# peer_id -> {endpoint, firma, timestamp_publicacion, ttl}
		self._tabla: Dict[str, dict] = {}

	def publicar_peer(self, peer_id: str, endpoint: str, firma: str, ttl: int) -> bool:
		"""
		Publica el endpoint firmado de un peer en la DHT.
		"""
		ahora = int(time.time())
		self._tabla[peer_id] = {
			"endpoint": endpoint,
			"firma": firma,
			"timestamp_publicacion": ahora,
			"ttl": ttl,
		}
		return True

	def buscar_peer(self, peer_id: str) -> Optional[dict]:
		"""
		Busca un peer por su peer_id y devuelve su endpoint y metadatos si existe y no expiró.
		"""
		registro = self._tabla.get(peer_id)
		if not registro:
			return None
		ahora = int(time.time())
		expiracion = registro["timestamp_publicacion"] + registro["ttl"]
		if ahora > expiracion:
			self._tabla.pop(peer_id, None)
			return None
		return registro

	def renovar_peer(self, peer_id: str, firma: str, ttl: int) -> bool:
		"""
		Renueva el TTL de un registro existente, validando la firma.
		"""
		registro = self._tabla.get(peer_id)
		if not registro:
			return False
		# Validar firma (placeholder, implementar verificación real)
		if registro["firma"] != firma:
			return False
		ahora = int(time.time())
		registro["timestamp_publicacion"] = ahora
		registro["ttl"] = ttl
		return True

	def limpiar_expirados(self) -> None:
		"""
		Elimina registros expirados de la DHT.
		"""
		ahora = int(time.time())
		expirados = [peer_id for peer_id, reg in self._tabla.items()
					 if ahora > reg["timestamp_publicacion"] + reg["ttl"]]
		for peer_id in expirados:
			self._tabla.pop(peer_id, None)
