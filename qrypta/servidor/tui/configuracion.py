"""TUI de configuracion.

Proposito: interfaz texto para operar el servidor.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: python -m servidor.tui.configuracion
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Footer, Header, Input, Static

from servidor.config.settings import settings

# ---------------------------------------------------------------------------
# Gestión de usuarios baneados (AdminTUI.2)
# ---------------------------------------------------------------------------

_USUARIOS_FILE = Path(__file__).resolve().parents[1] / "admin_consola" / "usuarios_ban.json"


def _cargarUsuarios() -> dict[str, dict]:
	"""Carga el registro de usuarios desde JSON persistente."""
	if not _USUARIOS_FILE.exists():
		return {}
	try:
		return json.loads(_USUARIOS_FILE.read_text(encoding="utf-8"))
	except (json.JSONDecodeError, OSError):
		return {}


def _guardarUsuarios(datos: dict[str, dict]) -> None:
	"""Guarda el registro de usuarios en el archivo JSON."""
	_USUARIOS_FILE.parent.mkdir(parents=True, exist_ok=True)
	_USUARIOS_FILE.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def listarUsuarios() -> list[dict]:
	"""Devuelve la lista de usuarios registrados."""
	return list(_cargarUsuarios().values())


def banearUsuario(userId: str, motivo: str = "ban manual") -> bool:
	"""Marca un usuario como baneado. Devuelve True si el cambio fue aplicado."""
	if not userId.strip():
		return False
	datos = _cargarUsuarios()
	datos[userId] = {"id": userId, "estado": "baneado", "motivo": motivo}
	_guardarUsuarios(datos)
	return True


def desbanearUsuario(userId: str) -> bool:
	"""Elimina el ban de un usuario. Devuelve True si estaba baneado."""
	datos = _cargarUsuarios()
	if userId not in datos:
		return False
	del datos[userId]
	_guardarUsuarios(datos)
	return True


# ---------------------------------------------------------------------------
# SQL Browser seguro (AdminTUI.3)
# ---------------------------------------------------------------------------

import csv
import io
import sqlite3

_DEFAULT_DB = Path(__file__).resolve().parents[1] / "servidor_mensajes.db"
_MAX_FILAS_SQL = 50


def _abrirDb(db_path: Path | None = None) -> sqlite3.Connection:
	ruta = db_path or _DEFAULT_DB
	if not ruta.exists():
		raise FileNotFoundError(f"Base de datos no encontrada: {ruta}")
	return sqlite3.connect(str(ruta))


def listarTablas(db_path: Path | None = None) -> list[str]:
	"""Devuelve los nombres de todas las tablas en la base de datos SQLite."""
	with _abrirDb(db_path) as conn:
		cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
		return [row[0] for row in cur.fetchall()]


def ejecutarSelectSeguro(query: str, db_path: Path | None = None) -> tuple[list[str], list[tuple]]:
	"""Ejecuta una consulta SELECT segura. Lanza ValueError si no es SELECT."""
	q = query.strip()
	if not q.upper().startswith("SELECT"):
		raise ValueError("Solo se permiten consultas SELECT en el SQL browser")
	with _abrirDb(db_path) as conn:
		cur = conn.execute(q)
		columnas = [desc[0] for desc in (cur.description or [])]
		filas = cur.fetchmany(_MAX_FILAS_SQL)
	return columnas, filas


def exportarCsv(tabla: str, db_path: Path | None = None) -> str:
	"""Exporta una tabla como CSV (cadena de texto). Valida nombre de tabla."""
	tablas_validas = listarTablas(db_path)
	if tabla not in tablas_validas:
		raise ValueError(f"Tabla no encontrada: {tabla}")
	columnas, filas = ejecutarSelectSeguro(f"SELECT * FROM {tabla}", db_path)
	buf = io.StringIO()
	writer = csv.writer(buf)
	writer.writerow(columnas)
	writer.writerows(filas)
	return buf.getvalue()


def exportarJson(tabla: str, db_path: Path | None = None) -> str:
	"""Exporta una tabla como JSON (Array de objetos). Valida nombre de tabla."""
	tablas_validas = listarTablas(db_path)
	if tabla not in tablas_validas:
		raise ValueError(f"Tabla no encontrada: {tabla}")
	columnas, filas = ejecutarSelectSeguro(f"SELECT * FROM {tabla}", db_path)
	registros = [dict(zip(columnas, fila)) for fila in filas]
	return json.dumps(registros, ensure_ascii=False, indent=2)


def rutaEnvLocal() -> Path:
	"""Devuelve la ruta del archivo .env operativo del servidor."""
	return Path(__file__).resolve().parents[1] / ".env"


def cargarEnvLocal() -> dict[str, str]:
	"""Carga variables simples KEY=VALUE desde el .env del servidor."""
	ruta = rutaEnvLocal()
	if not ruta.exists():
		return {}

	salida: dict[str, str] = {}
	for linea in ruta.read_text(encoding="utf-8").splitlines():
		linea = linea.strip()
		if not linea or linea.startswith("#") or "=" not in linea:
			continue
		clave, valor = linea.split("=", 1)
		salida[clave.strip()] = valor.strip()
	return salida


def guardarEnvLocal(valores: dict[str, str]) -> None:
	"""Guarda variables de entorno en formato .env."""
	ruta = rutaEnvLocal()
	lineas = [f"{k}={v}" for k, v in valores.items()]
	ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def ultimasLineas(ruta: Path, limite: int = 50) -> list[str]:
	"""Retorna las ultimas lineas de un archivo de texto."""
	if not ruta.exists():
		return []
	lineas = ruta.read_text(encoding="utf-8").splitlines()
	return lineas[-limite:]


class AppConfiguracion(App[None]):
	"""Interfaz en modo texto para operar configuración de servidor."""

	BINDINGS = [
		Binding("1", "ver_estado", "[1] Ver estado"),
		Binding("2", "configurar", "[2] Configurar"),
		Binding("3", "ver_logs", "[3] Ver logs"),
		Binding("4", "limpiar_mensajes", "[4] Limpiar mensajes"),
		Binding("5", "ver_metricas", "[5] Metricas"),
		Binding("6", "salir", "[6] Salir"),
		Binding("q", "salir", "Salir"),
	]

	CSS = """
	Screen {
		layout: vertical;
	}
	#panel {
		height: 1fr;
		border: round #666666;
		padding: 1;
	}
	#entrada {
		dock: bottom;
	}
	"""

	def compose(self) -> ComposeResult:
		yield Header(show_clock=True)
		with Vertical(id="panel"):
			yield Static(
				"Qrypta TUI\n"
				"Use teclas 1-6 o escriba comandos:\n"
				"help | ping | show config | set HOST=0.0.0.0 | set PUERTO=8000\n"
				"set TTL_MENSAJES_H=24 | set RATE_LIMIT=30/minute | tail 25",
				id="salida",
			)
			yield Input(placeholder="Comando", id="entrada")
		yield Footer()

	def on_input_submitted(self, event: Input.Submitted) -> None:
		comando = event.value.strip()
		event.input.value = ""
		self._procesarComando(comando)

	def _setSalida(self, texto: str) -> None:
		self.query_one("#salida", Static).update(texto)

	def _baseUrl(self) -> str:
		env = cargarEnvLocal()
		host = env.get("HOST", settings.host)
		puerto = env.get("PUERTO", str(settings.puerto))
		return f"http://{host}:{puerto}"

	def _procesarComando(self, comando: str) -> None:
		if not comando:
			return

		if comando.lower() == "help":
			self._setSalida(
				"Comandos disponibles:\n"
				"- help\n"
				"- ping (consulta /v1/estado)\n"
				"- show config\n"
				"- set HOST=... | PUERTO=... | TTL_MENSAJES_H=... | RATE_LIMIT=... | ADMIN_TOKEN=...\n"
				"- tail N (ultimas N lineas de auditoria, max 200)\n"
				"[Usuarios]\n"
				"- users list\n"
				"- ban <userId> [motivo]\n"
				"- unban <userId>\n"
				"[Rate limit]\n"
				"- rate show\n"
				"- rate set <N>/minute\n"
				"[SQL Browser]\n"
				"- sql tables\n"
				"- sql select <query>\n"
				"- export csv <tabla>\n"
				"- export json <tabla>"
			)
			return

		# ---- Gestión de usuarios (AdminTUI.2) --------------------------------
		if comando.lower() == "users list":
			usuarios = listarUsuarios()
			if not usuarios:
				self._setSalida("No hay usuarios registrados en el sistema local.")
				return
			lineas = [f"- {u['id']} [{u['estado']}] motivo: {u.get('motivo', '-')}" for u in usuarios]
			self._setSalida("Usuarios:\n" + "\n".join(lineas))
			return

		if comando.lower().startswith("ban "):
			partes = comando[4:].split(" ", 1)
			userId = partes[0].strip()
			motivo = partes[1].strip() if len(partes) > 1 else "ban manual"
			if not userId:
				self._setSalida("Uso: ban <userId> [motivo]")
				return
			banearUsuario(userId, motivo)
			self._setSalida(f"Usuario baneado: {userId} (motivo: {motivo})")
			return

		if comando.lower().startswith("unban "):
			userId = comando[6:].strip()
			if not userId:
				self._setSalida("Uso: unban <userId>")
				return
			ok = desbanearUsuario(userId)
			self._setSalida(f"Ban eliminado: {userId}" if ok else f"Usuario no encontrado: {userId}")
			return

		# ---- Rate limit (AdminTUI.2) -----------------------------------------
		if comando.lower() == "rate show":
			env = cargarEnvLocal()
			rate = env.get("RATE_LIMIT", settings.rateLimit if hasattr(settings, "rateLimit") else "30/minute")
			self._setSalida(f"Rate limit actual: {rate}")
			return

		if comando.lower().startswith("rate set "):
			valor = comando[9:].strip()
			if "/" not in valor:
				self._setSalida("Formato: rate set 30/minute")
				return
			env = cargarEnvLocal()
			env["RATE_LIMIT"] = valor
			guardarEnvLocal(env)
			self._setSalida(f"Rate limit actualizado: {valor}")
			return

		# ---- SQL Browser (AdminTUI.3) ----------------------------------------
		if comando.lower() == "sql tables":
			try:
				tablas = listarTablas()
				if not tablas:
					self._setSalida("No hay tablas en la base de datos.")
					return
				self._setSalida("Tablas:\n" + "\n".join(f"- {t}" for t in tablas))
			except FileNotFoundError as exc:
				self._setSalida(str(exc))
			return

		if comando.lower().startswith("sql select "):
			query = comando[11:].strip()
			try:
				columnas, filas = ejecutarSelectSeguro(query)
				cabecera = " | ".join(columnas)
				separador = "-" * len(cabecera)
				lineas = [cabecera, separador] + [" | ".join(str(v) for v in fila) for fila in filas]
				aviso = f"\n(mostrando max {_MAX_FILAS_SQL} filas)" if len(filas) == _MAX_FILAS_SQL else ""
				self._setSalida("\n".join(lineas) + aviso)
			except (ValueError, FileNotFoundError, sqlite3.Error) as exc:
				self._setSalida(f"Error SQL: {exc}")
			return

		if comando.lower().startswith("export csv "):
			tabla = comando[11:].strip()
			try:
				contenido = exportarCsv(tabla)
				self._setSalida(f"CSV de '{tabla}':\n{contenido[:2000]}")
			except (ValueError, FileNotFoundError) as exc:
				self._setSalida(f"Error export: {exc}")
			return

		if comando.lower().startswith("export json "):
			tabla = comando[12:].strip()
			try:
				contenido = exportarJson(tabla)
				self._setSalida(f"JSON de '{tabla}':\n{contenido[:2000]}")
			except (ValueError, FileNotFoundError) as exc:
				self._setSalida(f"Error export: {exc}")
			return

		if comando.lower() == "ping":
			self.action_ver_estado()
			return

		if comando.lower() == "show config":
			env = cargarEnvLocal()
			self._setSalida("Configuracion actual:\n" + json.dumps(env, ensure_ascii=True, indent=2))
			return

		if comando.lower().startswith("tail "):
			partes = comando.split(" ", 1)
			try:
				limite = max(1, min(200, int(partes[1].strip())))
			except ValueError:
				self._setSalida("Valor invalido. Use: tail 25")
				return
			rutaLog = Path(settings.logDir) / "auditoria.jsonl"
			lineas = ultimasLineas(rutaLog, limite=limite)
			if not lineas:
				self._setSalida("No hay logs para mostrar")
				return
			self._setSalida("\n".join(lineas))
			return

		if comando.lower().startswith("set ") and "=" in comando:
			cuerpo = comando[4:]
			clave, valor = cuerpo.split("=", 1)
			clave = clave.strip()
			valor = valor.strip()
			permitidas = {"HOST", "PUERTO", "TTL_MENSAJES_H", "RATE_LIMIT", "ADMIN_TOKEN"}
			if clave not in permitidas:
				self._setSalida(f"Clave no permitida: {clave}")
				return
			env = cargarEnvLocal()
			env[clave] = valor
			guardarEnvLocal(env)
			self._setSalida(f"Configuracion guardada: {clave}={valor}")
			return

		self._setSalida("Comando no reconocido")

	def action_ver_estado(self) -> None:
		try:
			with httpx.Client(timeout=5.0) as cliente:
				respuesta = cliente.get(f"{self._baseUrl()}/v1/estado")
				respuesta.raise_for_status()
			self._setSalida("Estado servidor:\n" + json.dumps(respuesta.json(), ensure_ascii=True, indent=2))
		except Exception as exc:  # pragma: no cover - depende de server vivo
			self._setSalida(f"No se pudo consultar estado: {exc}")

	def action_configurar(self) -> None:
		env = cargarEnvLocal()
		self._setSalida(
			"Modo configuracion. Use comandos set KEY=VALUE.\n"
			"Claves: HOST, PUERTO, TTL_MENSAJES_H, RATE_LIMIT, ADMIN_TOKEN\n"
			f"Actual: {json.dumps(env, ensure_ascii=True)}"
		)

	def action_ver_metricas(self) -> None:
		try:
			with httpx.Client(timeout=5.0) as cliente:
				estado = cliente.get(f"{self._baseUrl()}/v1/estado")
				estado.raise_for_status()
			datos = estado.json()
			self._setSalida(
				"Metricas operativas:\n"
				f"- Version: {datos.get('version', '-') }\n"
				f"- Uptime (s): {datos.get('uptimeS', '-') }\n"
				f"- Mensajes en cola: {datos.get('mensajesPendientes', '-') }\n"
				f"- Timestamp: {datos.get('timestamp', '-') }"
			)
		except Exception as exc:  # pragma: no cover - depende de server vivo
			self._setSalida(f"No se pudieron consultar metricas: {exc}")

	def action_ver_logs(self) -> None:
		rutaLog = Path(settings.logDir) / "auditoria.jsonl"
		lineas = ultimasLineas(rutaLog, limite=50)
		if not lineas:
			self._setSalida("No hay logs para mostrar")
			return
		self._setSalida("\n".join(lineas))

	def action_limpiar_mensajes(self) -> None:
		token = os.getenv("ADMIN_TOKEN") or cargarEnvLocal().get("ADMIN_TOKEN") or settings.adminToken
		try:
			with httpx.Client(timeout=5.0) as cliente:
				respuesta = cliente.delete(
					f"{self._baseUrl()}/v1/admin/mensajes",
					headers={"X-Admin-Token": token},
				)
				respuesta.raise_for_status()
			self._setSalida("Mensajes pendientes eliminados")
		except Exception as exc:  # pragma: no cover - depende de server vivo
			self._setSalida(f"No se pudo limpiar mensajes: {exc}")

	def action_salir(self) -> None:
		self.exit()


def main() -> None:
	"""Punto de entrada para ejecutar la TUI."""
	AppConfiguracion().run()


if __name__ == "__main__":
	main()
