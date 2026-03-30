import pytest
from fastapi.testclient import TestClient
from servidor.main import app
from pathlib import Path
import json

def test_dashboard_html():
    client = TestClient(app)
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert "Qrypta Admin" in resp.text
    assert "Auditoría" in resp.text

def test_auditoria_html():
    client = TestClient(app)
    resp = client.get("/dashboard/auditoria")
    assert resp.status_code == 200
    assert "Auditoría reciente" in resp.text
    assert "Cargando eventos" in resp.text or "No hay eventos" in resp.text

def test_audit_reciente_endpoint():
    client = TestClient(app)
    resp = client.get("/v1/admin/audit/reciente")
    assert resp.status_code == 200
    # Debe mostrar al menos un evento de ejemplo
    assert "Servidor iniciado correctamente" in resp.text
    assert "Usuario alice registrado" in resp.text
    assert "Intento de login fallido" in resp.text
    assert "Error de conexión" in resp.text
    assert "Backup realizado exitosamente" in resp.text

def test_audit_parser_unit():
    # Simula lectura de eventos.jsonl
    eventos = []
    path = Path(__file__).parent.parent / "auditoria" / "eventos.jsonl"
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            ev = json.loads(line)
            eventos.append(ev)
    assert len(eventos) >= 5
    tipos = {e["tipo"] for e in eventos}
    assert "INFO" in tipos
    assert "EXITO" in tipos
    assert "ADVERTENCIA" in tipos
    assert "ERROR" in tipos
