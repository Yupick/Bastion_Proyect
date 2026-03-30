"""API Auditoría Admin: Endpoints para panel avanzado de auditoría y métricas (Fase 12)."""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter()

# Ruta del log de auditoría (ajustar si es necesario)
RUTA_LOG = Path("servidor/logs/auditoria.jsonl")

@router.get("/v1/auditoria/eventos")
async def listar_eventos(limit: int = 100):
    try:
        with RUTA_LOG.open("r", encoding="utf-8") as f:
            lineas = f.readlines()[-limit:]
        eventos = [json.loads(l) for l in lineas]
        return {"eventos": eventos}
    except Exception:
        raise HTTPException(status_code=500, detail="No se pudo leer el log de auditoría")

@router.get("/v1/auditoria/metricas")
async def metricas_auditoria():
    try:
        with RUTA_LOG.open("r", encoding="utf-8") as f:
            eventos = [json.loads(l) for l in f.readlines()]
        total = len(eventos)
        exitosos = sum(1 for e in eventos if e.get("exitoso"))
        fallidos = total - exitosos
        return {"total_eventos": total, "exitosos": exitosos, "fallidos": fallidos}
    except Exception:
        raise HTTPException(status_code=500, detail="No se pudo calcular métricas")

@router.delete("/v1/auditoria/limpiar")
async def limpiar_log():
    try:
        RUTA_LOG.write_text("")
        return {"ok": True}
    except Exception:
        raise HTTPException(status_code=500, detail="No se pudo limpiar el log")
