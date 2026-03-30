"""Tests para el modulo de mensajeria E2E.

Proposito: validar cifrado/descifrado de mensajes entre contactos.
Autor: Qrypta Team
Fecha: 2026-03-30
"""

import base64

import pytest

from nucleo_crypto.contactos.lista import Contacto
from nucleo_crypto.crypto.keygen import generarParDilithium, generarParKyber
from nucleo_crypto.identidad.registro import _calcularPeerId
from nucleo_crypto.mensajeria.mensaje import (
	ErrorMensaje,
	ErrorVerificacion,
	MensajeCifrado,
	cifrar_para_contacto,
	descifrar_de_contacto,
)


def _crear_contacto_test(alias: str = "Alice") -> tuple[Contacto, bytes, bytes]:
	"""Helper para crear un contacto de prueba con sus claves."""
	pubkey_kyber, privkey_kyber = generarParKyber()
	pubkey_dilithium, privkey_dilithium = generarParDilithium()
	peer_id = _calcularPeerId(pubkey_dilithium)
	
	contacto = Contacto(
		peerId=peer_id,
		pubkeyKyberB64=base64.b64encode(pubkey_kyber).decode(),
		pubkeyDilithiumB64=base64.b64encode(pubkey_dilithium).decode(),
		aliasVerificado=False,
		fechaAgregado="2026-03-30T00:00:00Z",
		alias={"nombre": alias, "timestamp": "2026-03-30T00:00:00Z"},
	)
	
	return contacto, privkey_kyber, privkey_dilithium


def test_cifrar_y_descifrar_mensaje_exitoso():
	"""Test de cifrado y descifrado exitoso entre dos contactos."""
	# Crear Alice (emisora)
	contacto_alice, privkey_kyber_alice, privkey_dilithium_alice = _crear_contacto_test("Alice")
	peer_id_alice = bytes.fromhex(contacto_alice.peerId)
	
	# Crear Bob (receptor)
	contacto_bob, privkey_kyber_bob, _ = _crear_contacto_test("Bob")
	peer_id_bob = bytes.fromhex(contacto_bob.peerId)
	
	# Alice cifra mensaje para Bob
	contenido_original = b"Hola Bob! Este es un mensaje secreto."
	mensaje_cifrado = cifrar_para_contacto(
		contenido_original,
		peer_id_alice,
		contacto_bob,
		privkey_dilithium_alice,
	)
	
	# Verificar estructura del mensaje
	assert mensaje_cifrado.peer_id_origen == peer_id_alice
	assert mensaje_cifrado.peer_id_destino == peer_id_bob
	assert len(mensaje_cifrado.texto_cifrado_kyber) == 1088  # Kyber768
	assert len(mensaje_cifrado.nonce) == 12
	assert len(mensaje_cifrado.tag) == 16
	assert mensaje_cifrado.timestamp > 0
	
	# Bob descifra el mensaje de Alice
	contenido_descifrado = descifrar_de_contacto(
		mensaje_cifrado,
		contacto_alice,
		peer_id_bob,
		privkey_kyber_bob,
	)
	
	assert contenido_descifrado == contenido_original


def test_serializacion_mensaje():
	"""Test de serializacion y deserializacion de mensaje."""
	contacto_alice, _, privkey_dilithium_alice = _crear_contacto_test("Alice")
	peer_id_alice = bytes.fromhex(contacto_alice.peerId)
	
	contacto_bob, _, _ = _crear_contacto_test("Bob")
	
	# Crear mensaje
	mensaje_original = cifrar_para_contacto(
		b"Contenido de prueba",
		peer_id_alice,
		contacto_bob,
		privkey_dilithium_alice,
	)
	
	# Serializar
	bytes_serializados = mensaje_original.serializar()
	
	# Deserializar
	mensaje_restaurado = MensajeCifrado.deserializar(bytes_serializados)
	
	assert mensaje_restaurado.peer_id_origen == mensaje_original.peer_id_origen
	assert mensaje_restaurado.peer_id_destino == mensaje_original.peer_id_destino
	assert mensaje_restaurado.timestamp == mensaje_original.timestamp
	assert mensaje_restaurado.texto_cifrado_kyber == mensaje_original.texto_cifrado_kyber
	assert mensaje_restaurado.nonce == mensaje_original.nonce
	assert mensaje_restaurado.ciphertext == mensaje_original.ciphertext
	assert mensaje_restaurado.tag == mensaje_original.tag
	assert mensaje_restaurado.firma_dilithium == mensaje_original.firma_dilithium


def test_to_dict_y_from_dict():
	"""Test de conversion a/desde diccionario."""
	contacto_alice, _, privkey_dilithium_alice = _crear_contacto_test("Alice")
	peer_id_alice = bytes.fromhex(contacto_alice.peerId)
	
	contacto_bob, _, _ = _crear_contacto_test("Bob")
	
	mensaje_original = cifrar_para_contacto(
		b"Test dict",
		peer_id_alice,
		contacto_bob,
		privkey_dilithium_alice,
	)
	
	# Convertir a dict
	dict_mensaje = mensaje_original.to_dict()
	
	assert "peer_id_origen" in dict_mensaje
	assert "peer_id_destino" in dict_mensaje
	assert "timestamp" in dict_mensaje
	assert "ciphertext" in dict_mensaje
	
	# Restaurar desde dict
	mensaje_restaurado = MensajeCifrado.from_dict(dict_mensaje)
	
	assert mensaje_restaurado.peer_id_origen == mensaje_original.peer_id_origen
	assert mensaje_restaurado.ciphertext == mensaje_original.ciphertext


def test_firma_invalida_rechazada():
	"""Test que rechaza mensajes con firma invalida."""
	contacto_alice, _, privkey_dilithium_alice = _crear_contacto_test("Alice")
	peer_id_alice = bytes.fromhex(contacto_alice.peerId)
	
	contacto_bob, privkey_kyber_bob, _ = _crear_contacto_test("Bob")
	peer_id_bob = bytes.fromhex(contacto_bob.peerId)
	
	# Crear contacto falso (impostor)
	contacto_impostor, _, _ = _crear_contacto_test("Impostor")
	
	# Alice cifra mensaje para Bob
	mensaje = cifrar_para_contacto(
		b"Mensaje genuino",
		peer_id_alice,
		contacto_bob,
		privkey_dilithium_alice,
	)
	
	# Bob intenta descifrar usando clave del impostor (firma no coincidira)
	with pytest.raises(ErrorVerificacion, match="Firma del mensaje invalida"):
		descifrar_de_contacto(
			mensaje,
			contacto_impostor,  # Contacto incorrecto
			peer_id_bob,
			privkey_kyber_bob,
		)


def test_mensaje_modificado_rechazado():
	"""Test que rechaza mensajes modificados (tag AES-GCM invalido)."""
	contacto_alice, _, privkey_dilithium_alice = _crear_contacto_test("Alice")
	peer_id_alice = bytes.fromhex(contacto_alice.peerId)
	
	contacto_bob, privkey_kyber_bob, _ = _crear_contacto_test("Bob")
	peer_id_bob = bytes.fromhex(contacto_bob.peerId)
	
	mensaje = cifrar_para_contacto(
		b"Mensaje original",
		peer_id_alice,
		contacto_bob,
		privkey_dilithium_alice,
	)
	
	# Modificar el ciphertext (esto invalidara el tag AES-GCM)
	mensaje_modificado = MensajeCifrado(
		peer_id_origen=mensaje.peer_id_origen,
		peer_id_destino=mensaje.peer_id_destino,
		timestamp=mensaje.timestamp,
		texto_cifrado_kyber=mensaje.texto_cifrado_kyber,
		nonce=mensaje.nonce,
		ciphertext=b"x" * len(mensaje.ciphertext),  # Modificado
		tag=mensaje.tag,
		firma_dilithium=mensaje.firma_dilithium,
	)
	
	# Esto fallara en la verificacion de firma primero (firma no cubre el nuevo ciphertext)
	with pytest.raises(ErrorVerificacion):
		descifrar_de_contacto(
			mensaje_modificado,
			contacto_alice,
			peer_id_bob,
			privkey_kyber_bob,
		)


def test_mensaje_para_otro_destinatario_rechazado():
	"""Test que rechaza mensajes no dirigidos al receptor."""
	contacto_alice, _, privkey_dilithium_alice = _crear_contacto_test("Alice")
	peer_id_alice = bytes.fromhex(contacto_alice.peerId)
	
	contacto_bob, _, _ = _crear_contacto_test("Bob")
	
	contacto_charlie, privkey_kyber_charlie, _ = _crear_contacto_test("Charlie")
	peer_id_charlie = bytes.fromhex(contacto_charlie.peerId)
	
	# Alice cifra mensaje para Bob
	mensaje_para_bob = cifrar_para_contacto(
		b"Hola Bob",
		peer_id_alice,
		contacto_bob,
		privkey_dilithium_alice,
	)
	
	# Charlie intenta descifrar mensaje dirigido a Bob
	with pytest.raises(ErrorMensaje, match="El mensaje no esta dirigido a este peer"):
		descifrar_de_contacto(
			mensaje_para_bob,
			contacto_alice,
			peer_id_charlie,  # Charlie, no Bob
			privkey_kyber_charlie,
		)


def test_mensaje_de_contacto_inesperado_rechazado():
	"""Test que rechaza mensajes que no vienen del contacto esperado."""
	contacto_alice, _, privkey_dilithium_alice = _crear_contacto_test("Alice")
	peer_id_alice = bytes.fromhex(contacto_alice.peerId)
	
	contacto_bob, privkey_kyber_bob, _ = _crear_contacto_test("Bob")
	peer_id_bob = bytes.fromhex(contacto_bob.peerId)
	
	contacto_charlie, _, _ = _crear_contacto_test("Charlie")
	
	# Alice cifra mensaje para Bob
	mensaje = cifrar_para_contacto(
		b"Hola Bob",
		peer_id_alice,
		contacto_bob,
		privkey_dilithium_alice,
	)
	
	# Bob intenta descifrar pero espera un mensaje de Charlie
	with pytest.raises(ErrorMensaje, match="El mensaje no viene del contacto esperado"):
		descifrar_de_contacto(
			mensaje,
			contacto_charlie,  # Espera mensaje de Charlie, no Alice
			peer_id_bob,
			privkey_kyber_bob,
		)


def test_mensaje_vacio():
	"""Test de cifrado/descifrado de mensaje vacio."""
	contacto_alice, _, privkey_dilithium_alice = _crear_contacto_test("Alice")
	peer_id_alice = bytes.fromhex(contacto_alice.peerId)
	
	contacto_bob, privkey_kyber_bob, _ = _crear_contacto_test("Bob")
	peer_id_bob = bytes.fromhex(contacto_bob.peerId)
	
	# Cifrar mensaje vacio
	mensaje = cifrar_para_contacto(
		b"",
		peer_id_alice,
		contacto_bob,
		privkey_dilithium_alice,
	)
	
	# Descifrar
	contenido = descifrar_de_contacto(
		mensaje,
		contacto_alice,
		peer_id_bob,
		privkey_kyber_bob,
	)
	
	assert contenido == b""


def test_mensaje_largo():
	"""Test de cifrado/descifrado de mensaje grande."""
	contacto_alice, _, privkey_dilithium_alice = _crear_contacto_test("Alice")
	peer_id_alice = bytes.fromhex(contacto_alice.peerId)
	
	contacto_bob, privkey_kyber_bob, _ = _crear_contacto_test("Bob")
	peer_id_bob = bytes.fromhex(contacto_bob.peerId)
	
	# Mensaje de 1 MB
	contenido_largo = b"A" * (1024 * 1024)
	
	mensaje = cifrar_para_contacto(
		contenido_largo,
		peer_id_alice,
		contacto_bob,
		privkey_dilithium_alice,
	)
	
	contenido_descifrado = descifrar_de_contacto(
		mensaje,
		contacto_alice,
		peer_id_bob,
		privkey_kyber_bob,
	)
	
	assert contenido_descifrado == contenido_largo


def test_peer_id_invalido():
	"""Test que rechaza peer_id de longitud incorrecta."""
	contacto_bob, _, _ = _crear_contacto_test("Bob")
	_, _, privkey_dilithium = _crear_contacto_test("Alice")
	
	# peer_id muy corto
	with pytest.raises(ErrorMensaje, match="peer_id_origen debe tener 32 bytes"):
		cifrar_para_contacto(
			b"mensaje",
			b"corto",  # Menos de 32 bytes
			contacto_bob,
			privkey_dilithium,
		)


def test_deserializacion_mensaje_truncado():
	"""Test que rechaza deserializacion de mensaje truncado."""
	datos_truncados = b"abc"
	
	with pytest.raises(ErrorMensaje, match="Mensaje demasiado corto"):
		MensajeCifrado.deserializar(datos_truncados)


def test_conversacion_bidireccional():
	"""Test de conversacion bidireccional entre dos peers."""
	# Crear Alice y Bob
	contacto_alice, privkey_kyber_alice, privkey_dilithium_alice = _crear_contacto_test("Alice")
	peer_id_alice = bytes.fromhex(contacto_alice.peerId)
	
	contacto_bob, privkey_kyber_bob, privkey_dilithium_bob = _crear_contacto_test("Bob")
	peer_id_bob = bytes.fromhex(contacto_bob.peerId)
	
	# Alice -> Bob
	msg_alice_a_bob = cifrar_para_contacto(
		b"Hola Bob!",
		peer_id_alice,
		contacto_bob,
		privkey_dilithium_alice,
	)
	
	contenido_bob = descifrar_de_contacto(
		msg_alice_a_bob,
		contacto_alice,
		peer_id_bob,
		privkey_kyber_bob,
	)
	
	assert contenido_bob == b"Hola Bob!"
	
	# Bob -> Alice (respuesta)
	msg_bob_a_alice = cifrar_para_contacto(
		b"Hola Alice!",
		peer_id_bob,
		contacto_alice,
		privkey_dilithium_bob,
	)
	
	contenido_alice = descifrar_de_contacto(
		msg_bob_a_alice,
		contacto_bob,
		peer_id_alice,
		privkey_kyber_alice,
	)
	
	assert contenido_alice == b"Hola Alice!"
