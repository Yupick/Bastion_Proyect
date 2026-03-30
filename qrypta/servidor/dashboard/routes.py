from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

AUDIT_LOG_PATH = Path(__file__).parent.parent / "auditoria" / "eventos.jsonl"

COLOR_MAP = {
    "INFO": "border-blue-400",
    "EXITO": "border-green-400",
    "ADVERTENCIA": "border-yellow-400",
    "ERROR": "border-red-400",
}

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/dashboard/auditoria", response_class=HTMLResponse)
def auditoria(request: Request):
    return templates.TemplateResponse("auditoria.html", {"request": request})

@router.get("/v1/admin/audit/reciente", response_class=HTMLResponse)
def audit_reciente(request: Request):
    eventos = []
    if AUDIT_LOG_PATH.exists():
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            for line in list(f)[-20:][::-1]:
                try:
                    ev = json.loads(line)
                    eventos.append({
                        "tipo": ev.get("tipo", "INFO"),
                        "timestamp": ev.get("timestamp", "-"),
                        "detalle": ev.get("detalle", ""),
                        "color": COLOR_MAP.get(ev.get("tipo", "INFO"), "border-blue-400")
                    })
                except Exception:
                    continue
    return templates.TemplateResponse("audit_log.html", {"request": request, "eventos": eventos})
