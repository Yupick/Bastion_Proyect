"""API Push y Presencia: Endpoints para notificaciones push y control de presencia (Fase 10)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

# Simulación de almacenamiento en memoria para tokens y presencia
_tokens: Dict[str, str] = {}  # peer_id -> token_push
_presencia: Dict[str, bool] = {}  # peer_id -> online/offline

class RegistrarTokenRequest(BaseModel):
    peer_id: str
    token_push: str

class BajaTokenRequest(BaseModel):
    peer_id: str

class EnviarPushRequest(BaseModel):
    peer_id: str
    mensaje: str  # Solo para pruebas, en producción solo aviso sin contenido

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
    # Aquí se integraría con FCM/APNs
    # Solo simula el envío
    return {"ok": True, "detalle": f"Push enviado a {req.peer_id}"}

@router.get("/v1/presencia/{peer_id}")
async def consultar_presencia(peer_id: str):
    online = _presencia.get(peer_id, False)
    return {"peer_id": peer_id, "online": online}

@router.post("/v1/presencia/actualizar/{peer_id}")
async def actualizar_presencia(peer_id: str, online: bool):
    _presencia[peer_id] = online
    return {"ok": True, "peer_id": peer_id, "online": online}
