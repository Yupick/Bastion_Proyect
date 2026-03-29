"""Configuracion del servidor.

Proposito: centralizar variables de entorno.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: from servidor.config.settings import settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    host: str = "0.0.0.0"
    puerto: int = 8000
    modoDebug: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Configuracion()
