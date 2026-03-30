"""Rutas WebSocket y HTTP para sesiones E2E, grupos y archivos en Qrypta."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from .sesiones import GestorSesiones
from .archivos import validar_archivo, ArchivoInvalido
from pathlib import Path
import os
import uuid

router = APIRouter()
gestor = GestorSesiones()

# Conexiones activas: {sesion_id: {peer_id: websocket}}
conexiones = {}

UPLOAD_DIR = Path(__file__).parent.parent / "archivos_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@router.websocket("/ws/v1/sesion/{sesion_id}/{peer_id}")
async def ws_sesion(websocket: WebSocket, sesion_id: str, peer_id: str):
    await websocket.accept()
    if sesion_id not in conexiones:
        conexiones[sesion_id] = {}
    conexiones[sesion_id][peer_id] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            tipo = data.get("tipo")
            if tipo == "mensaje":
                # Broadcast a todos los miembros
                for pid, ws in conexiones[sesion_id].items():
                    if ws.application_state.value == 1:  # CONNECTED
                        await ws.send_json(data)
            elif tipo == "archivo":
                # Mensaje de control para notificar archivo (metadatos)
                for pid, ws in conexiones[sesion_id].items():
                    if ws.application_state.value == 1:
                        await ws.send_json(data)
            # Otros tipos: join, leave, etc.
    except WebSocketDisconnect:
        conexiones[sesion_id].pop(peer_id, None)
        if not conexiones[sesion_id]:
            conexiones.pop(sesion_id, None)

@router.post("/api/v1/archivo/upload/{sesion_id}/{peer_id}")
async def upload_archivo(sesion_id: str, peer_id: str, file: UploadFile = File(...)):
    try:
        validar_archivo(file.filename, file.spool_max_size or 0)
    except ArchivoInvalido as e:
        raise HTTPException(status_code=400, detail=str(e))
    ext = Path(file.filename).suffix
    nombre = f"{uuid.uuid4().hex}{ext}"
    ruta = UPLOAD_DIR / nombre
    with open(ruta, "wb") as f:
        contenido = await file.read()
        f.write(contenido)
    return {"ok": True, "filename": nombre, "size": len(contenido)}

@router.get("/api/v1/archivo/download/{filename}")
async def download_archivo(filename: str):
    ruta = UPLOAD_DIR / filename
    if not ruta.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(ruta, filename=filename)
