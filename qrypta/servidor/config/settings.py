"""Configuracion del servidor.

Proposito: centralizar variables de entorno.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: from servidor.config.settings import settings
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    host: str = Field(default="0.0.0.0", alias="HOST")
    puerto: int = Field(default=8000, alias="PUERTO")
    modoDebug: bool = Field(default=True, alias="MODO_DEBUG")
    ttlMensajesHoras: int = Field(default=24, alias="TTL_MENSAJES_H")
    maxMensajesPorPeer: int = Field(default=500, alias="MAX_MENSAJES_POR_PEER")
    rateLimit: str = Field(default="30/minute", alias="RATE_LIMIT")
    logDir: str = Field(default="qrypta/servidor/logs", alias="LOG_DIR")
    adminToken: str = Field(default="qrypta-admin-dev", alias="ADMIN_TOKEN")
    corsOrigins: str = Field(default="*", alias="CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=(".env", "qrypta/servidor/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


settings = Configuracion()


def obtenerCorsOrigins() -> list[str]:
    """Convierte el valor CSV de CORS en lista usable por FastAPI."""
    valores = [item.strip() for item in settings.corsOrigins.split(",") if item.strip()]
    return valores or ["*"]
