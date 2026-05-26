"""API Push y Presencia: Endpoints para notificaciones push y control de presencia (Fase 10)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict

from servidor.api.modelos import PATRON_PEER_ID
from servidor.push.notificaciones import (
    TIPO_AVISO_MENSAJE_PENDIENTE,
    construir_payload_aviso,
    enviar_a_proveedor,
)

router = APIRouter()

# Simulación de almacenamiento en memoria para tokens y presencia
_tokens: Dict[str, str] = {}  # peer_id -> token_push
_presencia: Dict[str, bool] = {}  # peer_id -> online/offline
_historial_envios: list[dict[str, str]] = []

class RegistrarTokenRequest(BaseModel):
    peer_id: str = Field(pattern=PATRON_PEER_ID)
    token_push: str = Field(min_length=8, max_length=512)

class BajaTokenRequest(BaseModel):
    peer_id: str = Field(pattern=PATRON_PEER_ID)

class EnviarPushRequest(BaseModel):
    peer_id: str = Field(pattern=PATRON_PEER_ID)
    tipo_aviso: str = Field(default=TIPO_AVISO_MENSAJE_PENDIENTE, min_length=3, max_length=64)


def resetear_estado_push() -> None:
    """Reinicia almacenamiento en memoria (uso en tests)."""
    _tokens.clear()
    _presencia.clear()
    _historial_envios.clear()

@router.post("/v1/push/registrar")
async def registrar_token(req: RegistrarTokenRequest):
    _tokens[req.peer_id] = req.token_push
    return {"ok": True}

@router.post("/v1/push/baja")
async def baja_token(req: BajaTokenRequest):
    _tokens.pop(req.peer_id, None)
    return {"ok": True}

@router.post("/v1/push/enviar")
async def enviar_push(req: EnviarPushRequest):
    token = _tokens.get(req.peer_id)
    if not token:
        raise HTTPException(status_code=404, detail="Token no registrado")

    payload = construir_payload_aviso(peer_id=req.peer_id, tipo_aviso=req.tipo_aviso)
    ok = enviar_a_proveedor(token_push=token, payload=payload)
    if not ok:
        raise HTTPException(status_code=502, detail="Error al enviar push")

    _historial_envios.append(payload)
    return {"ok": True, "detalle": f"Aviso push enviado a {req.peer_id}", "tipo": req.tipo_aviso}

@router.get("/v1/presencia/{peer_id}")
async def consultar_presencia(peer_id: str):
    online = _presencia.get(peer_id, False)
    return {"peer_id": peer_id, "online": online}

@router.post("/v1/presencia/actualizar/{peer_id}")
async def actualizar_presencia(peer_id: str, online: bool):
    _presencia[peer_id] = online
    return {"ok": True, "peer_id": peer_id, "online": online}
