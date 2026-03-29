"""Modelos API.

Proposito: definir contratos de entrada/salida.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: import desde rutas.py
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

PATRON_PEER_ID = r"^[a-f0-9]{64}$"


class MensajeEntrada(BaseModel):
    peerIdOrigen: str = Field(pattern=PATRON_PEER_ID)
    peerIdDestino: str = Field(pattern=PATRON_PEER_ID)
    payloadCifradoB64: str
    timestamp: datetime
    firmaB64: str


class MensajeSalida(BaseModel):
    id: UUID
    peerIdOrigen: str = Field(pattern=PATRON_PEER_ID)
    payloadCifradoB64: str
    timestamp: datetime
    firmaB64: str


class RespuestaEstado(BaseModel):
    version: str
    timestamp: datetime
    mensajesPendientes: int
    uptimeS: int


class RespuestaOk(BaseModel):
    ok: bool
    mensaje: str
