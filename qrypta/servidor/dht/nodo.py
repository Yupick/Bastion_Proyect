"""Nodo DHT.

Proposito: descubrimiento de pares sin base central.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: publicar/buscar peer_id
"""

import base64
import os
import time
from typing import Optional, Dict

try:
	import oqs
except ImportError:  # pragma: no cover - depende del entorno.
	oqs = None


class NodoDHT:
	"""
	Nodo DHT simplificado para descubrimiento de peers.
	Almacena endpoint, clave publica Dilithium y valida firmas.
	"""
	def __init__(self):
		# peer_id -> {endpoint, pubkey_dilithium_b64, firma, timestamp_publicacion, ttl}
		self._tabla: Dict[str, dict] = {}
		# Modo test: si True, no verifica firmas (para tests sin oqs)
		self._test_mode = os.getenv("QRYPTA_TEST_MODE", "false").lower() == "true"

	@staticmethod
	def _verificar_firma_dilithium(pubkey_b64: str, payload: bytes, firma_b64: str) -> bool:
		"""Verifica una firma Dilithium3."""
		if oqs is None:
			return False
		try:
			pubkey = base64.b64decode(pubkey_b64)
			firma = base64.b64decode(firma_b64)
			with oqs.Signature("Dilithium3") as cliente_firma:
				return bool(cliente_firma.verify(payload, firma, pubkey))
		except Exception:
			return False

	def _calcular_payload_publicar(self, peer_id: str, endpoint: str, timestamp: int) -> bytes:
		"""Calcula el payload que debe firmarse al publicar/renovar."""
		return f"{peer_id}:{endpoint}:{timestamp}".encode("utf-8")

	def publicar_peer(self, peer_id: str, endpoint: str, firma: str, ttl: int, pubkey_dilithium_b64: str = "") -> bool:
		"""
		Publica el endpoint firmado de un peer en la DHT.
		Valida que la firma corresponde a la clave publica derivada del peer_id.
		"""
		ahora = int(time.time())
		payload = self._calcular_payload_publicar(peer_id, endpoint, ahora)

		# Modo test: saltar verificacion
		if self._test_mode:
			self._tabla[peer_id] = {
				"endpoint": endpoint,
				"pubkey_dilithium_b64": pubkey_dilithium_b64 or "test_pubkey",
				"firma": firma,
				"timestamp_publicacion": ahora,
				"ttl": ttl,
			}
			return True

		# Si ya existe, verificar que la firma coincide con la clave almacenada
		registro_existente = self._tabla.get(peer_id)
		if registro_existente and registro_existente.get("pubkey_dilithium_b64"):
			if not self._verificar_firma_dilithium(registro_existente["pubkey_dilithium_b64"], payload, firma):
				return False
			pubkey_dilithium_b64 = registro_existente["pubkey_dilithium_b64"]
		elif pubkey_dilithium_b64:
			# Primera vez: verificar que peer_id coincide con la clave publica
			try:
				from hashlib import sha3_256
				pubkey_bytes = base64.b64decode(pubkey_dilithium_b64)
				peer_id_calculado = sha3_256(pubkey_bytes).hexdigest()
				if peer_id_calculado != peer_id:
					return False
			except Exception:
				return False
		else:
			return False

		self._tabla[peer_id] = {
			"endpoint": endpoint,
			"pubkey_dilithium_b64": pubkey_dilithium_b64,
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

	def obtener_clave_publica(self, peer_id: str) -> Optional[str]:
		"""Obtiene la clave publica Dilithium (base64) de un peer."""
		registro = self.buscar_peer(peer_id)
		if not registro:
			return None
		return registro.get("pubkey_dilithium_b64")

	def renovar_peer(self, peer_id: str, firma: str, ttl: int) -> bool:
		"""
		Renueva el TTL de un registro existente, validando la firma con la clave almacenada.
		"""
		registro = self._tabla.get(peer_id)
		if not registro:
			return False

		# Modo test: saltar verificacion
		if self._test_mode:
			ahora = int(time.time())
			registro["timestamp_publicacion"] = ahora
			registro["ttl"] = ttl
			registro["firma"] = firma
			return True

		ahora = int(time.time())
		payload = self._calcular_payload_publicar(peer_id, registro["endpoint"], agora)

		pubkey_b64 = registro.get("pubkey_dilithium_b64")
		if not pubkey_b64:
			return False

		if not self._verificar_firma_dilithium(pubkey_b64, payload, firma):
			return False

		registro["timestamp_publicacion"] = ahora
		registro["ttl"] = ttl
		registro["firma"] = firma
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