"""Logger de auditoria.

Proposito: registrar eventos sin informacion sensible.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: auditor.registrarEvento(...)
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from servidor.config.settings import settings


class AuditorLogger:
	"""Registra eventos auditables sin datos personales ni contenido."""

	def __init__(self, rutaLog: Path | None = None) -> None:
		carpetaLogs = Path(settings.logDir)
		carpetaLogs.mkdir(parents=True, exist_ok=True)
		self.rutaLog = rutaLog or (carpetaLogs / "auditoria.jsonl")

	def registrarEvento(self, evento: str, tamanoBytes: int, exitoso: bool) -> None:
		"""Registra evento mínimo verificable en formato JSONL."""
		timestamp = datetime.now(UTC).replace(microsecond=0).isoformat()
		hashTimestamp = hashlib.sha256(timestamp.encode("utf-8")).hexdigest()
		linea = {
			"evento": evento,
			"tamanoBytes": tamanoBytes,
			"exitoso": exitoso,
			"hashTimestamp": hashTimestamp,
		}
		with self.rutaLog.open("a", encoding="utf-8") as archivo:
			archivo.write(json.dumps(linea, ensure_ascii=True) + "\n")


auditor = AuditorLogger()
