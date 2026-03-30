"""API Grupos E2E: Endpoints para gestión de grupos y cifrado extremo a extremo (Fase 11)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List

router = APIRouter()

# Simulación de almacenamiento en memoria para grupos
_grupos: Dict[str, dict] = {}  # grupo_id -> {admin, miembros, clave_grupo, mensajes}

class CrearGrupoRequest(BaseModel):
    grupo_id: str
    admin: str
    miembros: List[str]
    clave_grupo: str  # En producción, cifrada para cada miembro

class MensajeGrupoRequest(BaseModel):
    grupo_id: str
    remitente: str
    payload_cifrado: str

class RotarClaveRequest(BaseModel):
    grupo_id: str
    nueva_clave: str

@router.post("/v1/grupos/crear")
async def crear_grupo(req: CrearGrupoRequest):
    if req.grupo_id in _grupos:
        raise HTTPException(status_code=400, detail="Grupo ya existe")
    _grupos[req.grupo_id] = {
        "admin": req.admin,
        "miembros": set(req.miembros),
        "clave_grupo": req.clave_grupo,
        "mensajes": []
    }
    return {"ok": True}

@router.post("/v1/grupos/mensaje")
async def enviar_mensaje_grupo(req: MensajeGrupoRequest):
    grupo = _grupos.get(req.grupo_id)
    if not grupo or req.remitente not in grupo["miembros"]:
        raise HTTPException(status_code=404, detail="Grupo o remitente inválido")
    grupo["mensajes"].append({"remitente": req.remitente, "payload": req.payload_cifrado})
    return {"ok": True}

@router.post("/v1/grupos/rotar_clave")
async def rotar_clave(req: RotarClaveRequest):
    grupo = _grupos.get(req.grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    grupo["clave_grupo"] = req.nueva_clave
    return {"ok": True}

@router.get("/v1/grupos/{grupo_id}/mensajes")
async def obtener_mensajes_grupo(grupo_id: str):
    grupo = _grupos.get(grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return grupo["mensajes"]
