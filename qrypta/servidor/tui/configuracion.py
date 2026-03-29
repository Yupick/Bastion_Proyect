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
		Binding("5", "salir", "[5] Salir"),
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
				"Use teclas 1-5 o escriba comandos: \n"
				"set HOST=0.0.0.0 | set PUERTO=8000 | set TTL_MENSAJES_H=24 | set RATE_LIMIT=30/minute\n"
				"show config",
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

		if comando.lower() == "show config":
			env = cargarEnvLocal()
			self._setSalida("Configuracion actual:\n" + json.dumps(env, ensure_ascii=True, indent=2))
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
