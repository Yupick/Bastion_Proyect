"""Servidor Qrypta.

Proposito: punto de entrada de la API.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: uvicorn servidor.main:app --reload
"""

from fastapi import FastAPI

app = FastAPI(title="Qrypta Server", version="0.1.0")


@app.get("/v1/estado")
def obtenerEstado() -> dict:
    return {"ok": True, "mensaje": "servidor activo"}
