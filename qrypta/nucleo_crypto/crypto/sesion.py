"""Sesion E2E.

Proposito: establecer y mantener sesiones con ratchet PQC.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: iniciarSesion(...)
"""

from __future__ import annotations

import json
import os
import struct
import time
from dataclasses import dataclass
from typing import Any

from . import firma, kem, simetrico


@dataclass
class SesionE2E:
	"""Sesion end-to-end con criptografia post-cuantica.
	
	Atributos:
		peer_id_local: ID del peer local (32 bytes)
		peer_id_remoto: ID del peer remoto (32 bytes)
		clave_sesion: Clave simetrica de la sesion (32 bytes)
		contador_envio: Contador de mensajes enviados
		contador_recepcion: Contador de mensajes recibidos
		ventana_desorden: Ventana de tolerancia a mensajes fuera de orden (default 100)
		mensajes_recibidos: Set de contadores ya procesados
		timestamp_creacion: Timestamp de creacion de la sesion
	"""
	
	peer_id_local: bytes
	peer_id_remoto: bytes
	clave_sesion: bytes
	contador_envio: int = 0
	contador_recepcion: int = 0
	ventana_desorden: int = 100
	mensajes_recibidos: set[int] | None = None
	timestamp_creacion: float | None = None
	
	def __post_init__(self) -> None:
		if self.mensajes_recibidos is None:
			self.mensajes_recibidos = set()
		if self.timestamp_creacion is None:
			self.timestamp_creacion = time.time()


class ErrorSesion(Exception):
	"""Error base para operaciones de sesion."""


class ErrorHandshake(ErrorSesion):
	"""Error durante el handshake de sesion."""


class ErrorContador(ErrorSesion):
	"""Error de validacion de contador de mensaje."""


class ErrorDescifrado(ErrorSesion):
	"""Error al descifrar mensaje de sesion."""


def iniciar_sesion_iniciador(
	peer_id_local: bytes,
	peer_id_remoto: bytes,
	clave_publica_kyber_remoto: bytes,
	clave_privada_dilithium_local: bytes,
) -> tuple[SesionE2E, bytes]:
	"""Inicia una sesion E2E como iniciador (Alice).
	
	Args:
		peer_id_local: ID del peer local (32 bytes)
		peer_id_remoto: ID del peer remoto (32 bytes)
		clave_publica_kyber_remoto: Clave publica Kyber del peer remoto
		clave_privada_dilithium_local: Clave privada Dilithium local
	
	Returns:
		(sesion, paquete_handshake) donde:
		- sesion: SesionE2E inicializada
		- paquete_handshake: bytes a enviar al peer remoto
	"""
	if len(peer_id_local) != 32 or len(peer_id_remoto) != 32:
		raise ErrorHandshake("peer_id debe tener 32 bytes")
	
	# Encapsular secreto compartido con Kyber
	texto_cifrado_kyber, secreto_compartido = kem.encapsular(clave_publica_kyber_remoto)
	
	# Derivar clave de sesion del secreto compartido
	contexto = b"qrypta_sesion_v1" + peer_id_local + peer_id_remoto
	clave_sesion = simetrico.derivarClave(secreto_compartido, contexto)
	
	# Crear estructura del handshake: peer_id_local + texto_cifrado_kyber
	payload_handshake = peer_id_local + texto_cifrado_kyber
	
	# Firmar el handshake con Dilithium
	firma_handshake = firma.firmar(payload_handshake, clave_privada_dilithium_local)
	
	# Paquete final: payload + firma
	paquete_handshake = payload_handshake + firma_handshake
	
	# Crear sesion
	sesion = SesionE2E(
		peer_id_local=peer_id_local,
		peer_id_remoto=peer_id_remoto,
		clave_sesion=clave_sesion,
	)
	
	return sesion, paquete_handshake


def aceptar_sesion_receptor(
	peer_id_local: bytes,
	paquete_handshake: bytes,
	clave_privada_kyber_local: bytes,
	clave_publica_dilithium_remoto: bytes,
) -> SesionE2E:
	"""Acepta una sesion E2E como receptor (Bob).
	
	Args:
		peer_id_local: ID del peer local (32 bytes)
		paquete_handshake: Paquete recibido del iniciador
		clave_privada_kyber_local: Clave privada Kyber local
		clave_publica_dilithium_remoto: Clave publica Dilithium del peer remoto
	
	Returns:
		sesion: SesionE2E inicializada
	"""
	if len(peer_id_local) != 32:
		raise ErrorHandshake("peer_id_local debe tener 32 bytes")
	
	# Extraer peer_id_remoto (primeros 32 bytes)
	if len(paquete_handshake) < 32:
		raise ErrorHandshake("Paquete handshake demasiado corto")
	
	peer_id_remoto = paquete_handshake[:32]
	
	# El texto cifrado Kyber tiene tamaño fijo (Kyber768: 1088 bytes)
	tamano_kyber = 1088
	if len(paquete_handshake) < 32 + tamano_kyber:
		raise ErrorHandshake("Paquete handshake no contiene texto cifrado Kyber completo")
	
	texto_cifrado_kyber = paquete_handshake[32:32 + tamano_kyber]
	firma_handshake = paquete_handshake[32 + tamano_kyber:]
	
	# Verificar firma
	payload_handshake = paquete_handshake[:32 + tamano_kyber]
	if not firma.verificar(payload_handshake, firma_handshake, clave_publica_dilithium_remoto):
		raise ErrorHandshake("Firma de handshake invalida")
	
	# Desencapsular secreto compartido
	secreto_compartido = kem.desencapsular(clave_privada_kyber_local, texto_cifrado_kyber)
	
	# Derivar clave de sesion (mismo contexto que el iniciador)
	contexto = b"qrypta_sesion_v1" + peer_id_remoto + peer_id_local
	clave_sesion = simetrico.derivarClave(secreto_compartido, contexto)
	
	# Crear sesion
	sesion = SesionE2E(
		peer_id_local=peer_id_local,
		peer_id_remoto=peer_id_remoto,
		clave_sesion=clave_sesion,
	)
	
	return sesion


def cifrar_mensaje(sesion: SesionE2E, contenido: bytes) -> bytes:
	"""Cifra un mensaje usando la sesion E2E.
	
	Args:
		sesion: Sesion E2E activa
		contenido: Contenido a cifrar
	
	Returns:
		paquete_cifrado: contador (8 bytes) + nonce (12 bytes) + cifrado + tag (16 bytes)
	"""
	# Incrementar contador de envio
	contador = sesion.contador_envio
	sesion.contador_envio += 1
	
	# Crear AAD (Additional Authenticated Data): peer_ids + contador
	aad = sesion.peer_id_local + sesion.peer_id_remoto + struct.pack("<Q", contador)
	
	# Cifrar con AES-256-GCM
	nonce, cifrado, tag = simetrico.cifrarAesGcm(contenido, sesion.clave_sesion, aad)
	
	# Paquete final: contador + nonce + cifrado + tag
	paquete_cifrado = struct.pack("<Q", contador) + nonce + cifrado + tag
	
	return paquete_cifrado


def descifrar_mensaje(sesion: SesionE2E, paquete_cifrado: bytes) -> bytes:
	"""Descifra un mensaje usando la sesion E2E.
	
	Args:
		sesion: Sesion E2E activa
		paquete_cifrado: Paquete cifrado recibido
	
	Returns:
		contenido: Contenido descifrado
	
	Raises:
		ErrorContador: Si el contador es invalido o duplicado
		ErrorDescifrado: Si la autenticacion falla
	"""
	# Extraer contador (8 bytes)
	if len(paquete_cifrado) < 8 + 12 + 16:  # contador + nonce + tag minimo
		raise ErrorDescifrado("Paquete cifrado demasiado corto")
	
	contador = struct.unpack("<Q", paquete_cifrado[:8])[0]
	
	# Validar contador (prevenir replay attacks y mensajes antiguos)
	if contador in sesion.mensajes_recibidos:
		raise ErrorContador(f"Mensaje duplicado con contador {contador}")
	
	# Permitir ventana de desorden (aceptar mensajes fuera de orden dentro de la ventana)
	if contador < sesion.contador_recepcion:
		# Mensaje antiguo
		diferencia = sesion.contador_recepcion - contador
		if diferencia > sesion.ventana_desorden:
			raise ErrorContador(
				f"Mensaje demasiado antiguo: contador={contador}, "
				f"esperado>={sesion.contador_recepcion - sesion.ventana_desorden}"
			)
	else:
		# Actualizar contador de recepcion al mas alto visto
		sesion.contador_recepcion = max(sesion.contador_recepcion, contador + 1)
	
	# Marcar contador como procesado
	sesion.mensajes_recibidos.add(contador)
	
	# Limpiar contadores antiguos fuera de la ventana de desorden
	contador_minimo = sesion.contador_recepcion - sesion.ventana_desorden
	sesion.mensajes_recibidos = {
		c for c in sesion.mensajes_recibidos if c >= contador_minimo
	}
	
	# Extraer nonce, cifrado y tag
	nonce = paquete_cifrado[8:20]
	cifrado_y_tag = paquete_cifrado[20:]
	
	if len(cifrado_y_tag) < 16:
		raise ErrorDescifrado("Paquete no contiene tag de autenticacion")
	
	cifrado = cifrado_y_tag[:-16]
	tag = cifrado_y_tag[-16:]
	
	# Crear AAD
	aad = sesion.peer_id_remoto + sesion.peer_id_local + struct.pack("<Q", contador)
	
	# Descifrar
	try:
		contenido = simetrico.descifrarAesGcm(nonce, cifrado, tag, sesion.clave_sesion, aad)
	except Exception as e:
		raise ErrorDescifrado(f"Fallo al descifrar mensaje: {e}") from e
	
	return contenido


def serializar_sesion(sesion: SesionE2E) -> str:
	"""Serializa una sesion a JSON para persistencia.
	
	Args:
		sesion: Sesion a serializar
	
	Returns:
		json_str: Representacion JSON de la sesion
	"""
	datos: dict[str, Any] = {
		"peer_id_local": sesion.peer_id_local.hex(),
		"peer_id_remoto": sesion.peer_id_remoto.hex(),
		"clave_sesion": sesion.clave_sesion.hex(),
		"contador_envio": sesion.contador_envio,
		"contador_recepcion": sesion.contador_recepcion,
		"ventana_desorden": sesion.ventana_desorden,
		"mensajes_recibidos": list(sesion.mensajes_recibidos or []),
		"timestamp_creacion": sesion.timestamp_creacion,
	}
	return json.dumps(datos)


def deserializar_sesion(json_str: str) -> SesionE2E:
	"""Deserializa una sesion desde JSON.
	
	Args:
		json_str: Representacion JSON de la sesion
	
	Returns:
		sesion: SesionE2E restaurada
	"""
	datos = json.loads(json_str)
	
	return SesionE2E(
		peer_id_local=bytes.fromhex(datos["peer_id_local"]),
		peer_id_remoto=bytes.fromhex(datos["peer_id_remoto"]),
		clave_sesion=bytes.fromhex(datos["clave_sesion"]),
		contador_envio=datos["contador_envio"],
		contador_recepcion=datos["contador_recepcion"],
		ventana_desorden=datos["ventana_desorden"],
		mensajes_recibidos=set(datos["mensajes_recibidos"]),
		timestamp_creacion=datos["timestamp_creacion"],
	)
