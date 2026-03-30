"""Mensajes cifrados E2E.

Proposito: estructura y funciones para cifrar/descifrar mensajes entre peers.
Autor: Qrypta Team
Fecha: 2026-03-30
"""

from __future__ import annotations

import base64
import struct
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from nucleo_crypto.crypto import firma, kem, simetrico

if TYPE_CHECKING:
	from nucleo_crypto.contactos.lista import Contacto


class ErrorMensaje(Exception):
	"""Error base para operaciones de mensajeria."""


class ErrorVerificacion(ErrorMensaje):
	"""Error de verificacion de firma."""


@dataclass
class MensajeCifrado:
	"""Representa un mensaje cifrado E2E con estructura completa.
	
	Estructura del mensaje:
	- peer_id_origen (32 bytes): ID del peer que envio el mensaje
	- peer_id_destino (32 bytes): ID del peer que recibe el mensaje
	- timestamp (8 bytes): Timestamp de envio (unix time, uint64)
	- texto_cifrado_kyber (1088 bytes): Secreto encapsulado con Kyber768
	- nonce (12 bytes): Nonce para AES-GCM
	- ciphertext (variable): Contenido cifrado
	- tag (16 bytes): Tag de autenticacion AES-GCM
	- firma_dilithium (variable): Firma de todo lo anterior
	"""
	
	peer_id_origen: bytes  # 32 bytes
	peer_id_destino: bytes  # 32 bytes
	timestamp: int  # 8 bytes (unix time)
	texto_cifrado_kyber: bytes  # 1088 bytes (Kyber768)
	nonce: bytes  # 12 bytes
	ciphertext: bytes  # variable
	tag: bytes  # 16 bytes
	firma_dilithium: bytes  # variable (~2420 bytes para Dilithium3)
	
	def serializar(self) -> bytes:
		"""Serializa el mensaje a bytes para transmision."""
		payload = (
			self.peer_id_origen +
			self.peer_id_destino +
			struct.pack("<Q", self.timestamp) +
			self.texto_cifrado_kyber +
			self.nonce +
			self.ciphertext +
			self.tag
		)
		return payload + self.firma_dilithium
	
	@staticmethod
	def deserializar(data: bytes) -> MensajeCifrado:
		"""Deserializa un mensaje desde bytes.
		
		Args:
			data: Bytes del mensaje serializado
		
		Returns:
			MensajeCifrado: Mensaje deserializado
		
		Raises:
			ErrorMensaje: Si el formato es invalido
		"""
		tamano_minimo = 32 + 32 + 8 + 1088 + 12 + 16  # Sin contar ciphertext ni firma
		if len(data) < tamano_minimo:
			raise ErrorMensaje(f"Mensaje demasiado corto: {len(data)} bytes")
		
		offset = 0
		
		# Extraer campos fijos
		peer_id_origen = data[offset:offset + 32]
		offset += 32
		
		peer_id_destino = data[offset:offset + 32]
		offset += 32
		
		timestamp = struct.unpack("<Q", data[offset:offset + 8])[0]
		offset += 8
		
		texto_cifrado_kyber = data[offset:offset + 1088]
		offset += 1088
		
		nonce = data[offset:offset + 12]
		offset += 12
		
		# El resto es ciphertext + tag + firma
		# Firma Dilithium3 tiene ~2420 bytes
		# Tag AES-GCM tiene 16 bytes
		# Necesitamos al menos 16 + 2420 bytes mas
		if len(data) < offset + 16 + 2420:
			raise ErrorMensaje("Mensaje incompleto (falta tag o firma)")
		
		# Firma esta al final (tamaño variable, tipicamente ~2420 bytes)
		# Tag esta antes de la firma (16 bytes)
		# Ciphertext esta entre nonce y tag
		
		# Extraemos del final hacia atras
		firma_dilithium = data[-(2420):]  # Firma al final
		tag = data[-(2420 + 16):-(2420)]  # Tag antes de firma
		ciphertext = data[offset:-(2420 + 16)]  # Ciphertext entre nonce y tag
		
		return MensajeCifrado(
			peer_id_origen=peer_id_origen,
			peer_id_destino=peer_id_destino,
			timestamp=timestamp,
			texto_cifrado_kyber=texto_cifrado_kyber,
			nonce=nonce,
			ciphertext=ciphertext,
			tag=tag,
			firma_dilithium=firma_dilithium,
		)
	
	def to_dict(self) -> dict[str, str]:
		"""Convierte el mensaje a diccionario con valores base64 para JSON."""
		return {
			"peer_id_origen": self.peer_id_origen.hex(),
			"peer_id_destino": self.peer_id_destino.hex(),
			"timestamp": str(self.timestamp),
			"texto_cifrado_kyber": base64.b64encode(self.texto_cifrado_kyber).decode(),
			"nonce": base64.b64encode(self.nonce).decode(),
			"ciphertext": base64.b64encode(self.ciphertext).decode(),
			"tag": base64.b64encode(self.tag).decode(),
			"firma_dilithium": base64.b64encode(self.firma_dilithium).decode(),
		}
	
	@staticmethod
	def from_dict(data: dict[str, str]) -> MensajeCifrado:
		"""Crea un mensaje desde diccionario."""
		return MensajeCifrado(
			peer_id_origen=bytes.fromhex(data["peer_id_origen"]),
			peer_id_destino=bytes.fromhex(data["peer_id_destino"]),
			timestamp=int(data["timestamp"]),
			texto_cifrado_kyber=base64.b64decode(data["texto_cifrado_kyber"]),
			nonce=base64.b64decode(data["nonce"]),
			ciphertext=base64.b64decode(data["ciphertext"]),
			tag=base64.b64decode(data["tag"]),
			firma_dilithium=base64.b64decode(data["firma_dilithium"]),
		)


def cifrar_para_contacto(
	contenido: bytes,
	peer_id_origen: bytes,
	contacto_destino: Contacto,
	clave_privada_dilithium_origen: bytes,
) -> MensajeCifrado:
	"""Cifra un mensaje para un contacto usando Kyber + AES-256-GCM + Dilithium.
	
	Args:
		contenido: Contenido a cifrar (bytes)
		peer_id_origen: ID del peer que envia (32 bytes)
		contacto_destino: Contacto destinatario con claves publicas
		clave_privada_dilithium_origen: Clave privada Dilithium del origen
	
	Returns:
		MensajeCifrado: Mensaje cifrado y firmado listo para enviar
	"""
	if len(peer_id_origen) != 32:
		raise ErrorMensaje("peer_id_origen debe tener 32 bytes")
	
	# Obtener peer_id del destino (hex -> bytes)
	peer_id_destino = bytes.fromhex(contacto_destino.peerId)
	
	# Obtener clave publica Kyber del destinatario
	clave_publica_kyber_destino = base64.b64decode(contacto_destino.pubkeyKyberB64)
	
	# Encapsular secreto compartido con Kyber
	texto_cifrado_kyber, secreto_compartido = kem.encapsular(clave_publica_kyber_destino)
	
	# Derivar clave de cifrado del secreto compartido
	contexto = b"qrypta_mensaje_v1" + peer_id_origen + peer_id_destino
	clave_mensaje = simetrico.derivarClave(secreto_compartido, contexto)
	
	# Timestamp
	timestamp = int(time.time())
	
	# AAD (Additional Authenticated Data): peer_ids + timestamp
	aad = peer_id_origen + peer_id_destino + struct.pack("<Q", timestamp)
	
	# Cifrar contenido con AES-256-GCM
	nonce, ciphertext, tag = simetrico.cifrarAesGcm(contenido, clave_mensaje, aad)
	
	# Construir payload a firmar
	payload_firma = (
		peer_id_origen +
		peer_id_destino +
		struct.pack("<Q", timestamp) +
		texto_cifrado_kyber +
		nonce +
		ciphertext +
		tag
	)
	
	# Firmar con Dilithium
	firma_dilithium = firma.firmar(payload_firma, clave_privada_dilithium_origen)
	
	# Crear mensaje cifrado
	mensaje = MensajeCifrado(
		peer_id_origen=peer_id_origen,
		peer_id_destino=peer_id_destino,
		timestamp=timestamp,
		texto_cifrado_kyber=texto_cifrado_kyber,
		nonce=nonce,
		ciphertext=ciphertext,
		tag=tag,
		firma_dilithium=firma_dilithium,
	)
	
	return mensaje


def descifrar_de_contacto(
	mensaje: MensajeCifrado,
	contacto_origen: Contacto,
	peer_id_local: bytes,
	clave_privada_kyber_local: bytes,
) -> bytes:
	"""Descifra un mensaje de un contacto verificando su firma.
	
	Args:
		mensaje: Mensaje cifrado recibido
		contacto_origen: Contacto que envio el mensaje
		peer_id_local: ID del peer local (32 bytes)
		clave_privada_kyber_local: Clave privada Kyber local
	
	Returns:
		contenido: Contenido descifrado
	
	Raises:
		ErrorVerificacion: Si la firma no es valida
		ErrorMensaje: Si el descifrado falla
	"""
	if len(peer_id_local) != 32:
		raise ErrorMensaje("peer_id_local debe tener 32 bytes")
	
	# Verificar que el mensaje es para nosotros
	if mensaje.peer_id_destino != peer_id_local:
		raise ErrorMensaje("El mensaje no esta dirigido a este peer")
	
	# Verificar que el mensaje viene del contacto esperado
	peer_id_origen_esperado = bytes.fromhex(contacto_origen.peerId)
	if mensaje.peer_id_origen != peer_id_origen_esperado:
		raise ErrorMensaje("El mensaje no viene del contacto esperado")
	
	# Construir payload firmado
	payload_firma = (
		mensaje.peer_id_origen +
		mensaje.peer_id_destino +
		struct.pack("<Q", mensaje.timestamp) +
		mensaje.texto_cifrado_kyber +
		mensaje.nonce +
		mensaje.ciphertext +
		mensaje.tag
	)
	
	# Verificar firma con clave publica Dilithium del contacto
	clave_publica_dilithium_origen = base64.b64decode(contacto_origen.pubkeyDilithiumB64)
	
	if not firma.verificar(payload_firma, mensaje.firma_dilithium, clave_publica_dilithium_origen):
		raise ErrorVerificacion("Firma del mensaje invalida")
	
	# Desencapsular secreto compartido
	secreto_compartido = kem.desencapsular(clave_privada_kyber_local, mensaje.texto_cifrado_kyber)
	
	# Derivar clave de cifrado (mismo contexto que el emisor)
	contexto = b"qrypta_mensaje_v1" + mensaje.peer_id_origen + mensaje.peer_id_destino
	clave_mensaje = simetrico.derivarClave(secreto_compartido, contexto)
	
	# AAD
	aad = mensaje.peer_id_origen + mensaje.peer_id_destino + struct.pack("<Q", mensaje.timestamp)
	
	# Descifrar contenido
	try:
		contenido = simetrico.descifrarAesGcm(
			mensaje.nonce,
			mensaje.ciphertext,
			mensaje.tag,
			clave_mensaje,
			aad
		)
	except Exception as e:
		raise ErrorMensaje(f"Fallo al descifrar mensaje: {e}") from e
	
	return contenido
