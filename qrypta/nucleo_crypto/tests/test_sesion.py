"""Tests para el protocolo de sesion E2E.

Proposito: validar handshake, cifrado y descifrado de sesiones.
Autor: Qrypta Team
Fecha: 2026-03-30
"""

import pytest

from nucleo_crypto.crypto.keygen import generarParDilithium, generarParKyber
from nucleo_crypto.crypto.sesion import (
	ErrorContador,
	ErrorDescifrado,
	ErrorHandshake,
	SesionE2E,
	aceptar_sesion_receptor,
	cifrar_mensaje,
	descifrar_mensaje,
	deserializar_sesion,
	iniciar_sesion_iniciador,
	serializar_sesion,
)


def test_handshake_exitoso():
	"""Test de handshake completo entre Alice y Bob."""
	# Alice genera sus claves
	pubkey_kyber_alice, privkey_kyber_alice = generarParKyber()
	pubkey_dilithium_alice, privkey_dilithium_alice = generarParDilithium()
	peer_id_alice = b"A" * 32
	
	# Bob genera sus claves
	pubkey_kyber_bob, privkey_kyber_bob = generarParKyber()
	pubkey_dilithium_bob, privkey_dilithium_bob = generarParDilithium()
	peer_id_bob = b"B" * 32
	
	# Alice inicia sesion con Bob
	sesion_alice, paquete_handshake = iniciar_sesion_iniciador(
		peer_id_alice,
		peer_id_bob,
		pubkey_kyber_bob,
		privkey_dilithium_alice,
	)
	
	assert sesion_alice.peer_id_local == peer_id_alice
	assert sesion_alice.peer_id_remoto == peer_id_bob
	assert len(sesion_alice.clave_sesion) == 32
	assert sesion_alice.contador_envio == 0
	assert sesion_alice.contador_recepcion == 0
	
	# Bob acepta la sesion de Alice
	sesion_bob = aceptar_sesion_receptor(
		peer_id_bob,
		paquete_handshake,
		privkey_kyber_bob,
		pubkey_dilithium_alice,
	)
	
	assert sesion_bob.peer_id_local == peer_id_bob
	assert sesion_bob.peer_id_remoto == peer_id_alice
	assert len(sesion_bob.clave_sesion) == 32
	
	# Verificar que ambas sesiones tienen la misma clave
	assert sesion_alice.clave_sesion == sesion_bob.clave_sesion


def test_handshake_firma_invalida():
	"""Test que rechaza handshake con firma invalida."""
	pubkey_kyber_bob, _ = generarParKyber()
	_, privkey_dilithium_alice = generarParDilithium()
	_, privkey_kyber_bob = generarParKyber()
	pubkey_dilithium_otro, _ = generarParDilithium()  # Clave diferente
	
	peer_id_alice = b"A" * 32
	peer_id_bob = b"B" * 32
	
	_, paquete_handshake = iniciar_sesion_iniciador(
		peer_id_alice,
		peer_id_bob,
		pubkey_kyber_bob,
		privkey_dilithium_alice,
	)
	
	# Bob intenta verificar con clave publica diferente
	with pytest.raises(ErrorHandshake, match="Firma de handshake invalida"):
		aceptar_sesion_receptor(
			peer_id_bob,
			paquete_handshake,
			privkey_kyber_bob,
			pubkey_dilithium_otro,  # Clave incorrecta
		)


def test_cifrar_descifrar_mensaje():
	"""Test de cifrado y descifrado de mensaje en sesion."""
	# Setup de sesion
	pubkey_kyber_bob, privkey_kyber_bob = generarParKyber()
	pubkey_dilithium_alice, privkey_dilithium_alice = generarParDilithium()
	
	peer_id_alice = b"A" * 32
	peer_id_bob = b"B" * 32
	
	sesion_alice, paquete_handshake = iniciar_sesion_iniciador(
		peer_id_alice,
		peer_id_bob,
		pubkey_kyber_bob,
		privkey_dilithium_alice,
	)
	
	sesion_bob = aceptar_sesion_receptor(
		peer_id_bob,
		paquete_handshake,
		privkey_kyber_bob,
		pubkey_dilithium_alice,
	)
	
	# Alice envia mensaje a Bob
	mensaje_original = b"Hola Bob! Este es un mensaje secreto."
	paquete_cifrado = cifrar_mensaje(sesion_alice, mensaje_original)
	
	# Verificar que contador de Alice se incremento
	assert sesion_alice.contador_envio == 1
	
	# Bob descifra el mensaje
	mensaje_descifrado = descifrar_mensaje(sesion_bob, paquete_cifrado)
	
	assert mensaje_descifrado == mensaje_original
	assert sesion_bob.contador_recepcion == 1


def test_multiples_mensajes():
	"""Test de envio de multiples mensajes en sesion."""
	pubkey_kyber_bob, privkey_kyber_bob = generarParKyber()
	pubkey_dilithium_alice, privkey_dilithium_alice = generarParDilithium()
	
	peer_id_alice = b"A" * 32
	peer_id_bob = b"B" * 32
	
	sesion_alice, paquete_handshake = iniciar_sesion_iniciador(
		peer_id_alice,
		peer_id_bob,
		pubkey_kyber_bob,
		privkey_dilithium_alice,
	)
	
	sesion_bob = aceptar_sesion_receptor(
		peer_id_bob,
		paquete_handshake,
		privkey_kyber_bob,
		pubkey_dilithium_alice,
	)
	
	# Enviar 10 mensajes
	mensajes = [f"Mensaje {i}".encode() for i in range(10)]
	
	for i, msg in enumerate(mensajes):
		paquete = cifrar_mensaje(sesion_alice, msg)
		descifrado = descifrar_mensaje(sesion_bob, paquete)
		assert descifrado == msg
		assert sesion_alice.contador_envio == i + 1
		assert sesion_bob.contador_recepcion == i + 1


def test_replay_attack_detectado():
	"""Test que detecta ataques de replay."""
	pubkey_kyber_bob, privkey_kyber_bob = generarParKyber()
	pubkey_dilithium_alice, privkey_dilithium_alice = generarParDilithium()
	
	peer_id_alice = b"A" * 32
	peer_id_bob = b"B" * 32
	
	sesion_alice, paquete_handshake = iniciar_sesion_iniciador(
		peer_id_alice,
		peer_id_bob,
		pubkey_kyber_bob,
		privkey_dilithium_alice,
	)
	
	sesion_bob = aceptar_sesion_receptor(
		peer_id_bob,
		paquete_handshake,
		privkey_kyber_bob,
		pubkey_dilithium_alice,
	)
	
	# Enviar mensaje
	paquete = cifrar_mensaje(sesion_alice, b"mensaje original")
	descifrar_mensaje(sesion_bob, paquete)
	
	# Intentar reenviar el mismo paquete (replay)
	with pytest.raises(ErrorContador, match="Mensaje duplicado"):
		descifrar_mensaje(sesion_bob, paquete)


def test_mensajes_fuera_de_orden():
	"""Test de tolerancia a mensajes fuera de orden."""
	pubkey_kyber_bob, privkey_kyber_bob = generarParKyber()
	pubkey_dilithium_alice, privkey_dilithium_alice = generarParDilithium()
	
	peer_id_alice = b"A" * 32
	peer_id_bob = b"B" * 32
	
	sesion_alice, paquete_handshake = iniciar_sesion_iniciador(
		peer_id_alice,
		peer_id_bob,
		pubkey_kyber_bob,
		privkey_dilithium_alice,
	)
	
	sesion_bob = aceptar_sesion_receptor(
		peer_id_bob,
		paquete_handshake,
		privkey_kyber_bob,
		pubkey_dilithium_alice,
	)
	
	# Crear 3 mensajes
	paquetes = [
		cifrar_mensaje(sesion_alice, f"msg{i}".encode())
		for i in range(3)
	]
	
	# Recibir en orden: 0, 2, 1 (fuera de orden)
	assert descifrar_mensaje(sesion_bob, paquetes[0]) == b"msg0"
	assert descifrar_mensaje(sesion_bob, paquetes[2]) == b"msg2"  # Saltar msg1
	assert descifrar_mensaje(sesion_bob, paquetes[1]) == b"msg1"  # Llega tarde


def test_mensaje_antiguo_rechazado():
	"""Test que rechaza mensajes fuera de la ventana de tolerancia."""
	pubkey_kyber_bob, privkey_kyber_bob = generarParKyber()
	pubkey_dilithium_alice, privkey_dilithium_alice = generarParDilithium()
	
	peer_id_alice = b"A" * 32
	peer_id_bob = b"B" * 32
	
	sesion_alice, paquete_handshake = iniciar_sesion_iniciador(
		peer_id_alice,
		peer_id_bob,
		pubkey_kyber_bob,
		privkey_dilithium_alice,
	)
	
	sesion_bob = aceptar_sesion_receptor(
		peer_id_bob,
		paquete_handshake,
		privkey_kyber_bob,
		pubkey_dilithium_alice,
	)
	
	# Configurar ventana pequeña
	sesion_bob.ventana_desorden = 5
	
	# Enviar mensaje 0
	paquete_0 = cifrar_mensaje(sesion_alice, b"msg0")
	
	# Enviar mensajes 1-10
	for i in range(1, 11):
		paquete = cifrar_mensaje(sesion_alice, f"msg{i}".encode())
		descifrar_mensaje(sesion_bob, paquete)
	
	# Intentar procesar mensaje 0 (demasiado antiguo)
	with pytest.raises(ErrorContador, match="Mensaje demasiado antiguo"):
		descifrar_mensaje(sesion_bob, paquete_0)


def test_serializacion_sesion():
	"""Test de serializacion y deserializacion de sesion."""
	peer_id_local = b"L" * 32
	peer_id_remoto = b"R" * 32
	clave_sesion = b"K" * 32
	
	sesion_original = SesionE2E(
		peer_id_local=peer_id_local,
		peer_id_remoto=peer_id_remoto,
		clave_sesion=clave_sesion,
		contador_envio=42,
		contador_recepcion=100,
		ventana_desorden=200,
		mensajes_recibidos={95, 96, 97, 98, 99},
	)
	
	# Serializar
	json_str = serializar_sesion(sesion_original)
	
	# Deserializar
	sesion_restaurada = deserializar_sesion(json_str)
	
	assert sesion_restaurada.peer_id_local == peer_id_local
	assert sesion_restaurada.peer_id_remoto == peer_id_remoto
	assert sesion_restaurada.clave_sesion == clave_sesion
	assert sesion_restaurada.contador_envio == 42
	assert sesion_restaurada.contador_recepcion == 100
	assert sesion_restaurada.ventana_desorden == 200
	assert sesion_restaurada.mensajes_recibidos == {95, 96, 97, 98, 99}


def test_mensaje_truncado():
	"""Test que rechaza mensajes truncados."""
	pubkey_kyber_bob, privkey_kyber_bob = generarParKyber()
	pubkey_dilithium_alice, privkey_dilithium_alice = generarParDilithium()
	
	peer_id_alice = b"A" * 32
	peer_id_bob = b"B" * 32
	
	sesion_alice, paquete_handshake = iniciar_sesion_iniciador(
		peer_id_alice,
		peer_id_bob,
		pubkey_kyber_bob,
		privkey_dilithium_alice,
	)
	
	sesion_bob = aceptar_sesion_receptor(
		peer_id_bob,
		paquete_handshake,
		privkey_kyber_bob,
		pubkey_dilithium_alice,
	)
	
	paquete = cifrar_mensaje(sesion_alice, b"mensaje")
	
	# Truncar el paquete
	paquete_truncado = paquete[:10]
	
	with pytest.raises(ErrorDescifrado, match="Paquete cifrado demasiado corto"):
		descifrar_mensaje(sesion_bob, paquete_truncado)


def test_mensaje_modificado():
	"""Test que detecta modificacion del mensaje (tag invalido)."""
	pubkey_kyber_bob, privkey_kyber_bob = generarParKyber()
	pubkey_dilithium_alice, privkey_dilithium_alice = generarParDilithium()
	
	peer_id_alice = b"A" * 32
	peer_id_bob = b"B" * 32
	
	sesion_alice, paquete_handshake = iniciar_sesion_iniciador(
		peer_id_alice,
		peer_id_bob,
		pubkey_kyber_bob,
		privkey_dilithium_alice,
	)
	
	sesion_bob = aceptar_sesion_receptor(
		peer_id_bob,
		paquete_handshake,
		privkey_kyber_bob,
		pubkey_dilithium_alice,
	)
	
	paquete = bytearray(cifrar_mensaje(sesion_alice, b"mensaje"))
	
	# Modificar un byte en el cifrado
	paquete[25] ^= 0xFF
	
	with pytest.raises(ErrorDescifrado, match="Fallo al descifrar mensaje"):
		descifrar_mensaje(sesion_bob, bytes(paquete))
