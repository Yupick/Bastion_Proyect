"""Lista de contactos local.

Proposito: almacenar y verificar contactos localmente.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: agregarContacto(...)
"""

from __future__ import annotations

import base64
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from nucleo_crypto.almacenamiento.local import cargarIdentidad, guardarIdentidad, obtenerDirectorioBase
from nucleo_crypto.crypto.firma import verificar
from nucleo_crypto.identidad.alias import aliasDesdeDict, verificarAlias
from nucleo_crypto.identidad.registro import importarContacto

NOMBRE_ARCHIVO_CONTACTOS = "contactos.enc"


@dataclass
class Contacto:
	"""Representa un contacto de confianza guardado localmente."""

	peerId: str
	pubkeyKyberB64: str
	pubkeyDilithiumB64: str
	aliasVerificado: bool
	fechaAgregado: str
	alias: dict[str, str] | None = None


class ListaContactos:
	"""Gestiona contactos persistidos en almacenamiento cifrado local."""

	def __init__(self, ruta: Path | None = None) -> None:
		self.ruta = ruta or (obtenerDirectorioBase() / NOMBRE_ARCHIVO_CONTACTOS)
		self.contactos: dict[str, Contacto] = {}

	def cargar(self, contrasena: str) -> None:
		"""Carga contactos desde almacenamiento local cifrado."""
		if not self.ruta.exists():
			self.contactos = {}
			return
		datos = cargarIdentidad(contrasena, ruta=self.ruta)
		self.contactos = {
			item["peerId"]: Contacto(**item)
			for item in datos.get("contactos", [])
		}

	def guardar(self, contrasena: str) -> None:
		"""Guarda contactos en almacenamiento local cifrado."""
		datos = {"contactos": [asdict(contacto) for contacto in self.contactos.values()]}
		guardarIdentidad(datos, contrasena, ruta=self.ruta)

	def agregarContacto(self, datosPublicos: dict[str, Any]) -> Contacto:
		"""Agrega un contacto validando su estructura y alias opcional."""
		normalizado = importarContacto(datosPublicos)
		aliasDatos = normalizado.get("alias")
		aliasVerificado = False
		if isinstance(aliasDatos, dict):
			aliasObjeto = aliasDesdeDict(aliasDatos)
			clavePublica = base64.b64decode(str(normalizado["pubkeyDilithiumB64"]))
			aliasVerificado = verificarAlias(aliasObjeto, clavePublica)

		contacto = Contacto(
			peerId=str(normalizado["peerId"]),
			pubkeyKyberB64=str(normalizado["pubkeyKyberB64"]),
			pubkeyDilithiumB64=str(normalizado["pubkeyDilithiumB64"]),
			aliasVerificado=aliasVerificado,
			fechaAgregado=datetime.now(UTC).replace(microsecond=0).isoformat(),
			alias=aliasDatos if isinstance(aliasDatos, dict) else None,
		)
		self.contactos[contacto.peerId] = contacto
		return contacto

	def buscarPorPeerId(self, peerId: str) -> Contacto | None:
		"""Busca contacto por peer_id."""
		return self.contactos.get(peerId)


def verificarMensaje(mensaje: bytes, firmaB64: str, peerId: str, lista: ListaContactos) -> bool:
	"""Verifica la firma de un mensaje usando la clave del contacto."""
	contacto = lista.buscarPorPeerId(peerId)
	if contacto is None:
		return False
	clavePublica = base64.b64decode(contacto.pubkeyDilithiumB64)
	firmaDigital = base64.b64decode(firmaB64)
	return verificar(mensaje, firmaDigital, clavePublica)
