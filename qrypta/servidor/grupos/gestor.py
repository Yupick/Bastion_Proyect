"""Gestor de grupos.

Proposito: enrutar mensajes de grupo sin acceder al contenido.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: distribuir payload a miembros
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Grupo:
	grupo_id: str
	admin: str
	miembros: set[str] = field(default_factory=set)
	clave_grupo: str = ""
	mensajes: list[dict[str, str]] = field(default_factory=list)

	def es_admin(self, peer_id: str) -> bool:
		return peer_id == self.admin


_grupos: dict[str, Grupo] = {}


def resetear_estado_grupos() -> None:
	"""Reinicia el almacenamiento en memoria (uso en tests)."""
	_grupos.clear()


def crear_grupo(grupo_id: str, admin: str, miembros: list[str], clave_grupo: str) -> Grupo:
	if grupo_id in _grupos:
		raise ValueError("Grupo ya existe")
	grupo = Grupo(
		grupo_id=grupo_id,
		admin=admin,
		miembros=set(miembros) | {admin},
		clave_grupo=clave_grupo,
	)
	_grupos[grupo_id] = grupo
	return grupo


def obtener_grupo(grupo_id: str) -> Grupo | None:
	return _grupos.get(grupo_id)


def agregar_miembro(grupo_id: str, admin: str, miembro: str) -> Grupo:
	grupo = _grupos.get(grupo_id)
	if not grupo:
		raise LookupError("Grupo no encontrado")
	if not grupo.es_admin(admin):
		raise PermissionError("Solo el admin puede modificar miembros")
	grupo.miembros.add(miembro)
	return grupo


def remover_miembro(grupo_id: str, admin: str, miembro: str, nueva_clave: str) -> Grupo:
	grupo = _grupos.get(grupo_id)
	if not grupo:
		raise LookupError("Grupo no encontrado")
	if not grupo.es_admin(admin):
		raise PermissionError("Solo el admin puede modificar miembros")
	grupo.miembros.discard(miembro)
	grupo.clave_grupo = nueva_clave
	return grupo


def rotar_clave(grupo_id: str, admin: str, nueva_clave: str) -> Grupo:
	grupo = _grupos.get(grupo_id)
	if not grupo:
		raise LookupError("Grupo no encontrado")
	if not grupo.es_admin(admin):
		raise PermissionError("Solo el admin puede rotar la clave")
	grupo.clave_grupo = nueva_clave
	return grupo


def registrar_mensaje(grupo_id: str, remitente: str, payload_cifrado: str) -> dict[str, str]:
	grupo = _grupos.get(grupo_id)
	if not grupo:
		raise LookupError("Grupo no encontrado")
	if remitente not in grupo.miembros:
		raise PermissionError("Remitente no pertenece al grupo")
	mensaje = {"remitente": remitente, "payload": payload_cifrado}
	grupo.mensajes.append(mensaje)
	return mensaje


def listar_mensajes(grupo_id: str) -> list[dict[str, str]]:
	grupo = _grupos.get(grupo_id)
	if not grupo:
		raise LookupError("Grupo no encontrado")
	return list(grupo.mensajes)


def listar_miembros(grupo_id: str) -> set[str]:
	grupo = _grupos.get(grupo_id)
	if not grupo:
		raise LookupError("Grupo no encontrado")
	return set(grupo.miembros)
