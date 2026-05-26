"""Sincronizacion multi-dispositivo.

Proposito: vincular dispositivos, transferir estado inicial cifrado y revocar
dispositivos comprometidos sin exponer contenido en claro.
"""

from __future__ import annotations

import base64
import hmac
import json
import os
from dataclasses import dataclass, field
from hashlib import sha256

from nucleo_crypto.crypto.simetrico import cifrarAesGcm, descifrarAesGcm, derivarClave


class ErrorVinculoSincronizacion(Exception):
	"""Firma de vinculo invalida o dispositivo no autorizado."""


class ErrorDispositivoRevocado(Exception):
	"""El dispositivo fue revocado y no puede sincronizar."""


@dataclass
class DispositivoSincronizado:
	dispositivo_id: str
	activo: bool = True
	ultimo_evento: int = 0


@dataclass
class EventoSincronizacion:
	seq: int
	tipo: str
	dispositivo_id: str
	datos: dict[str, str] = field(default_factory=dict)


@dataclass
class EstadoSincronizacion:
	maestro_id: str
	secreto_maestro: bytes
	estado_inicial: dict[str, str]
	dispositivos: dict[str, DispositivoSincronizado] = field(default_factory=dict)
	eventos: list[EventoSincronizacion] = field(default_factory=list)
	secuencia_eventos: int = 0

	def _dispositivo_activo(self, dispositivo_id: str) -> DispositivoSincronizado:
		dispositivo = self.dispositivos.get(dispositivo_id)
		if not dispositivo or not dispositivo.activo:
			raise ErrorDispositivoRevocado("Dispositivo revocado o no vinculado")
		return dispositivo

	def _registrar_evento(self, tipo: str, dispositivo_id: str, datos: dict[str, str]) -> EventoSincronizacion:
		self.secuencia_eventos += 1
		evento = EventoSincronizacion(
			seq=self.secuencia_eventos,
			tipo=tipo,
			dispositivo_id=dispositivo_id,
			datos=datos,
		)
		self.eventos.append(evento)
		return evento


def _firmar_vinculo(secreto_maestro: bytes, dispositivo_id: str) -> str:
	return hmac.new(secreto_maestro, dispositivo_id.encode("utf-8"), sha256).hexdigest()


def _verificar_vinculo(secreto_maestro: bytes, dispositivo_id: str, firma_vinculo: str) -> None:
	esperada = _firmar_vinculo(secreto_maestro, dispositivo_id)
	if not hmac.compare_digest(esperada, firma_vinculo):
		raise ErrorVinculoSincronizacion("Firma de vinculo invalida")


def _serializar_estado(estado: dict[str, str]) -> bytes:
	return json.dumps(estado, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _deserializar_estado(contenido: bytes) -> dict[str, str]:
	return json.loads(contenido.decode("utf-8"))


def crear_estado_sincronizacion(
	maestro_id: str,
	estado_inicial: dict[str, str] | None = None,
	secreto_maestro: bytes | None = None,
) -> EstadoSincronizacion:
	return EstadoSincronizacion(
		maestro_id=maestro_id,
		secreto_maestro=secreto_maestro or os.urandom(32),
		estado_inicial=dict(estado_inicial or {}),
	)


def vincular_dispositivo(
	estado: EstadoSincronizacion,
	dispositivo_id: str,
	firma_vinculo: str,
) -> dict[str, str]:
	_verificar_vinculo(estado.secreto_maestro, dispositivo_id, firma_vinculo)
	if dispositivo_id in estado.dispositivos and estado.dispositivos[dispositivo_id].activo:
		raise ValueError("Dispositivo ya vinculado")

	clave_dispositivo = derivarClave(
		estado.secreto_maestro,
		f"sync:{dispositivo_id}".encode("utf-8"),
	)
	contenido = _serializar_estado(estado.estado_inicial)
	nonce, cifrado, tag = cifrarAesGcm(contenido, clave_dispositivo, aad=dispositivo_id.encode("utf-8"))

	estado.dispositivos[dispositivo_id] = DispositivoSincronizado(dispositivo_id=dispositivo_id)
	estado._registrar_evento("vinculo", dispositivo_id, {"estado": "inicial_transferido"})
	return {
		"dispositivo_id": dispositivo_id,
		"nonce_b64": base64.b64encode(nonce).decode("ascii"),
		"cifrado_b64": base64.b64encode(cifrado).decode("ascii"),
		"tag_b64": base64.b64encode(tag).decode("ascii"),
	}


def descifrar_estado_inicial(
	estado: EstadoSincronizacion,
	dispositivo_id: str,
	paquete: dict[str, str],
) -> dict[str, str]:
	dispositivo = estado._dispositivo_activo(dispositivo_id)
	_ = dispositivo
	clave_dispositivo = derivarClave(
		estado.secreto_maestro,
		f"sync:{dispositivo_id}".encode("utf-8"),
	)
	contenido = descifrarAesGcm(
		base64.b64decode(paquete["nonce_b64"]),
		base64.b64decode(paquete["cifrado_b64"]),
		base64.b64decode(paquete["tag_b64"]),
		clave_dispositivo,
		aad=dispositivo_id.encode("utf-8"),
	)
	return _deserializar_estado(contenido)


def registrar_mensaje(
	estado: EstadoSincronizacion,
	dispositivo_id: str,
	mensaje_id: str,
	leido: bool = False,
) -> EventoSincronizacion:
	estado._dispositivo_activo(dispositivo_id)
	return estado._registrar_evento(
		"mensaje", dispositivo_id, {"mensaje_id": mensaje_id, "leido": str(leido).lower()}
	)


def registrar_estado_lectura(
	estado: EstadoSincronizacion,
	dispositivo_id: str,
	mensaje_id: str,
) -> EventoSincronizacion:
	estado._dispositivo_activo(dispositivo_id)
	return estado._registrar_evento("lectura", dispositivo_id, {"mensaje_id": mensaje_id})


def sincronizar_dispositivo(
	estado: EstadoSincronizacion,
	dispositivo_id: str,
	ultimo_seq: int = 0,
) -> list[EventoSincronizacion]:
	device = estado._dispositivo_activo(dispositivo_id)
	eventos = [evento for evento in estado.eventos if evento.seq > ultimo_seq]
	device.ultimo_evento = estado.secuencia_eventos
	estado._registrar_evento("sync", dispositivo_id, {"eventos_enviados": str(len(eventos))})
	return eventos


def revocar_dispositivo(
	estado: EstadoSincronizacion,
	dispositivo_id: str,
	maestro_id: str,
	rotar_secreto: bool = True,
) -> bytes:
	if maestro_id != estado.maestro_id:
		raise PermissionError("Solo el maestro puede revocar dispositivos")
	if dispositivo_id not in estado.dispositivos:
		raise LookupError("Dispositivo no encontrado")

	estado.dispositivos[dispositivo_id].activo = False
	estado._registrar_evento("revocacion", dispositivo_id, {"rotar_secreto": str(rotar_secreto).lower()})

	if rotar_secreto:
		estado.secreto_maestro = os.urandom(32)
	return estado.secreto_maestro


def firmar_vinculo_dispositivo(estado: EstadoSincronizacion, dispositivo_id: str) -> str:
	return _firmar_vinculo(estado.secreto_maestro, dispositivo_id)