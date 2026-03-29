"""Modelos API.

Proposito: definir contratos de entrada/salida.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: import desde rutas.py
"""

from datetime import datetime

from pydantic import BaseModel, Field


class MensajeEntrada(BaseModel):
    peerIdOrigen: str = Field(min_length=64, max_length=64)
    peerIdDestino: str = Field(min_length=64, max_length=64)
    payloadCifradoB64: str
    timestamp: datetime
    firmaB64: str


class RespuestaEstado(BaseModel):
    ok: bool
    mensaje: str
