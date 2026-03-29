"""Gestion de alias.

Proposito: crear, actualizar y revocar alias firmados.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: crearAlias(...)
"""

from __future__ import annotations

import base64
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from nucleo_crypto.crypto import firma

ESTADO_ALIAS_ACTIVO = "activo"
ESTADO_ALIAS_REVOCADO = "revocado"


@dataclass
class Alias:
	"""Representa un alias firmado digitalmente."""

	nombre: str
	firmaB64: str
	timestampIso: str
	estado: str


def _normalizarPayload(nombre: str, timestampIso: str, estado: str) -> bytes:
	payload = {
		"nombre": nombre,
		"timestampIso": timestampIso,
		"estado": estado,
	}
	return json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("utf-8")


def crearAlias(nombre: str, clavePrivadaDilithium: bytes) -> Alias:
	"""Crea un alias activo firmado con Dilithium3."""
	timestampIso = datetime.now(UTC).replace(microsecond=0).isoformat()
	payload = _normalizarPayload(nombre, timestampIso, ESTADO_ALIAS_ACTIVO)
	firmaDigital = firma.firmar(payload, clavePrivadaDilithium)
	return Alias(
		nombre=nombre,
		firmaB64=base64.b64encode(firmaDigital).decode("ascii"),
		timestampIso=timestampIso,
		estado=ESTADO_ALIAS_ACTIVO,
	)


def revocarAlias(aliasActual: Alias, clavePrivadaDilithium: bytes) -> Alias:
	"""Revoca un alias existente y firma su nuevo estado."""
	timestampIso = datetime.now(UTC).replace(microsecond=0).isoformat()
	payload = _normalizarPayload(aliasActual.nombre, timestampIso, ESTADO_ALIAS_REVOCADO)
	firmaDigital = firma.firmar(payload, clavePrivadaDilithium)
	return Alias(
		nombre=aliasActual.nombre,
		firmaB64=base64.b64encode(firmaDigital).decode("ascii"),
		timestampIso=timestampIso,
		estado=ESTADO_ALIAS_REVOCADO,
	)


def actualizarAlias(aliasViejo: Alias, nuevoNombre: str, clavePrivadaDilithium: bytes) -> Alias:
	"""Actualiza el alias revocando el anterior y creando uno nuevo."""
	_ = revocarAlias(aliasViejo, clavePrivadaDilithium)
	return crearAlias(nuevoNombre, clavePrivadaDilithium)


def verificarAlias(aliasActual: Alias, clavePublicaDilithium: bytes) -> bool:
	"""Verifica la firma del alias con la clave publica del contacto."""
	payload = _normalizarPayload(aliasActual.nombre, aliasActual.timestampIso, aliasActual.estado)
	firmaDigital = base64.b64decode(aliasActual.firmaB64)
	return firma.verificar(payload, firmaDigital, clavePublicaDilithium)


def aliasADict(aliasActual: Alias) -> dict[str, str]:
	"""Serializa alias para persistencia o intercambio."""
	return asdict(aliasActual)


def aliasDesdeDict(datos: dict[str, str]) -> Alias:
	"""Deserializa alias desde un diccionario validado."""
	return Alias(
		nombre=datos["nombre"],
		firmaB64=datos["firmaB64"],
		timestampIso=datos["timestampIso"],
		estado=datos["estado"],
	)
