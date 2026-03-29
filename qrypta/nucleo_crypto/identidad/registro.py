"""Registro local de identidad.

Proposito: crear identidad sin contacto con servidor.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: registrarNuevoUsuario(...)
"""

from __future__ import annotations

import base64
import hashlib
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from nucleo_crypto.almacenamiento.local import guardarIdentidad
from nucleo_crypto.crypto.keygen import generarParDilithium, generarParKyber
from nucleo_crypto.identidad.alias import Alias, aliasADict, aliasDesdeDict, crearAlias
from nucleo_crypto.recuperacion.mnemonic import generarMnemonic


@dataclass
class RegistroUsuario:
	"""Representa la identidad local completa del usuario."""

	peerId: str
	pubkeyKyberB64: str
	privkeyKyberB64: str
	pubkeyDilithiumB64: str
	privkeyDilithiumB64: str
	alias: Alias | None
	fechaCreacion: str
	mnemonic24Palabras: list[str]


def _aB64(valorBytes: bytes) -> str:
	return base64.b64encode(valorBytes).decode("ascii")


def _deB64(valorB64: str) -> bytes:
	return base64.b64decode(valorB64)


def _calcularPeerId(clavePublicaDilithium: bytes) -> str:
	return hashlib.sha3_256(clavePublicaDilithium).hexdigest()


def registrarNuevoUsuario(contrasena: str, aliasNombre: str | None = None) -> RegistroUsuario:
	"""Registra un usuario local con claves PQC y alias opcional."""
	pubkeyKyber, privkeyKyber = generarParKyber()
	pubkeyDilithium, privkeyDilithium = generarParDilithium()
	_, palabras = generarMnemonic()

	aliasUsuario = None
	if aliasNombre:
		aliasUsuario = crearAlias(aliasNombre, privkeyDilithium)

	registro = RegistroUsuario(
		peerId=_calcularPeerId(pubkeyDilithium),
		pubkeyKyberB64=_aB64(pubkeyKyber),
		privkeyKyberB64=_aB64(privkeyKyber),
		pubkeyDilithiumB64=_aB64(pubkeyDilithium),
		privkeyDilithiumB64=_aB64(privkeyDilithium),
		alias=aliasUsuario,
		fechaCreacion=datetime.now(UTC).replace(microsecond=0).isoformat(),
		mnemonic24Palabras=palabras,
	)
	guardarRegistroLocal(registro, contrasena)
	return registro


def guardarRegistroLocal(registro: RegistroUsuario, contrasena: str) -> None:
	"""Persiste la identidad local cifrada."""
	datos = asdict(registro)
	if registro.alias is not None:
		datos["alias"] = aliasADict(registro.alias)
	guardarIdentidad(datos, contrasena)


def exportarClavePublica(registro: RegistroUsuario) -> dict[str, object]:
	"""Exporta la identidad publica para intercambio por QR/codigo/enlace."""
	datosPublicos: dict[str, object] = {
		"peerId": registro.peerId,
		"pubkeyKyberB64": registro.pubkeyKyberB64,
		"pubkeyDilithiumB64": registro.pubkeyDilithiumB64,
	}
	if registro.alias is not None:
		datosPublicos["alias"] = aliasADict(registro.alias)
	return datosPublicos


def importarContacto(datosPublicos: dict[str, object]) -> dict[str, object]:
	"""Valida y normaliza datos publicos de un contacto."""
	camposRequeridos = ["peerId", "pubkeyKyberB64", "pubkeyDilithiumB64"]
	faltantes = [campo for campo in camposRequeridos if campo not in datosPublicos]
	if faltantes:
		raise ValueError(f"Faltan campos requeridos: {', '.join(faltantes)}")

	peerId = str(datosPublicos["peerId"])
	if len(peerId) != 64:
		raise ValueError("peerId invalido: debe tener 64 caracteres hexadecimales.")

	_deB64(str(datosPublicos["pubkeyKyberB64"]))
	clavePublicaDilithium = _deB64(str(datosPublicos["pubkeyDilithiumB64"]))
	peerIdCalculado = _calcularPeerId(clavePublicaDilithium)
	if peerId != peerIdCalculado:
		raise ValueError("peerId invalido: no coincide con la clave publica Dilithium.")

	normalizado: dict[str, object] = {
		"peerId": peerId,
		"pubkeyKyberB64": str(datosPublicos["pubkeyKyberB64"]),
		"pubkeyDilithiumB64": str(datosPublicos["pubkeyDilithiumB64"]),
	}
	if "alias" in datosPublicos and isinstance(datosPublicos["alias"], dict):
		normalizado["alias"] = aliasADict(aliasDesdeDict(datosPublicos["alias"]))
	return normalizado
