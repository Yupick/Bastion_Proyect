"""API Grupos E2E: Endpoints para gestión de grupos y cifrado extremo a extremo (Fase 11)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from servidor.api.modelos import PATRON_PEER_ID
from servidor.grupos.gestor import (
	agregar_miembro,
    crear_grupo as crear_grupo_dominio,
	listar_mensajes,
	listar_miembros,
	registrar_mensaje,
	remover_miembro,
    rotar_clave as rotar_clave_dominio,
	resetear_estado_grupos,
)

router = APIRouter()

class CrearGrupoRequest(BaseModel):
    grupo_id: str = Field(min_length=3, max_length=64)
    admin: str = Field(pattern=PATRON_PEER_ID)
    miembros: list[str] = Field(default_factory=list)
    clave_grupo: str = Field(min_length=8, max_length=512)

class MensajeGrupoRequest(BaseModel):
    grupo_id: str = Field(min_length=3, max_length=64)
    remitente: str = Field(pattern=PATRON_PEER_ID)
    payload_cifrado: str = Field(min_length=1)

class RotarClaveRequest(BaseModel):
    grupo_id: str = Field(min_length=3, max_length=64)
    admin: str = Field(pattern=PATRON_PEER_ID)
    nueva_clave: str = Field(min_length=8, max_length=512)

class AgregarMiembroRequest(BaseModel):
    grupo_id: str = Field(min_length=3, max_length=64)
    admin: str = Field(pattern=PATRON_PEER_ID)
    miembro: str = Field(pattern=PATRON_PEER_ID)

class RemoverMiembroRequest(BaseModel):
    grupo_id: str = Field(min_length=3, max_length=64)
    admin: str = Field(pattern=PATRON_PEER_ID)
    miembro: str = Field(pattern=PATRON_PEER_ID)
    nueva_clave: str = Field(min_length=8, max_length=512)


def resetear_estado_grupos_api() -> None:
    """Reinicia almacenamiento en memoria (uso en tests)."""
    resetear_estado_grupos()

@router.post("/v1/grupos/crear")
async def crear_grupo(req: CrearGrupoRequest):
    try:
	    grupo = crear_grupo_dominio(req.grupo_id, req.admin, req.miembros, req.clave_grupo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "grupo_id": grupo.grupo_id, "miembros": len(grupo.miembros)}


@router.post("/v1/grupos/agregar_miembro")
async def agregar_miembro_grupo(req: AgregarMiembroRequest):
    try:
        grupo = agregar_miembro(req.grupo_id, req.admin, req.miembro)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"ok": True, "miembros": sorted(grupo.miembros)}


@router.post("/v1/grupos/remover_miembro")
async def remover_miembro_grupo(req: RemoverMiembroRequest):
    try:
        grupo = remover_miembro(req.grupo_id, req.admin, req.miembro, req.nueva_clave)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"ok": True, "miembros": sorted(grupo.miembros)}

@router.post("/v1/grupos/mensaje")
async def enviar_mensaje_grupo(req: MensajeGrupoRequest):
    try:
        mensaje = registrar_mensaje(req.grupo_id, req.remitente, req.payload_cifrado)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"ok": True, "mensaje": mensaje}

@router.post("/v1/grupos/rotar_clave")
async def rotar_clave(req: RotarClaveRequest):
    try:
	    grupo = rotar_clave_dominio(req.grupo_id, req.admin, req.nueva_clave)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"ok": True, "clave_actualizada": True}

@router.get("/v1/grupos/{grupo_id}/mensajes")
async def obtener_mensajes_grupo(grupo_id: str):
    try:
        return listar_mensajes(grupo_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/v1/grupos/{grupo_id}/miembros")
async def obtener_miembros_grupo(grupo_id: str):
    try:
        return {"grupo_id": grupo_id, "miembros": sorted(listar_miembros(grupo_id))}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
