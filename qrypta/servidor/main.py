"""Servidor Qrypta.

Proposito: punto de entrada de la API.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: uvicorn servidor.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from servidor.api.rutas import router
from servidor.ws import routes as ws_routes
from servidor.config.settings import obtenerCorsOrigins

app = FastAPI(title="Qrypta Server", version="0.1.0")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=obtenerCorsOrigins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
app.include_router(ws_routes.router)

_rutaStatic = Path(__file__).resolve().parent / "api" / "dashboard" / "static"
_rutaDashboard = Path(__file__).resolve().parent / "api" / "dashboard" / "index.html"
if _rutaStatic.exists():
    app.mount("/dashboard/static", StaticFiles(directory=_rutaStatic), name="dashboard-static")


@app.get("/dashboard", include_in_schema=False)
async def dashboard() -> FileResponse:
    """Sirve un dashboard básico de estado."""
    return FileResponse(_rutaDashboard)
