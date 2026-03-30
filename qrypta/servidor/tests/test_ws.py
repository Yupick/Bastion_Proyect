import pytest
from fastapi.testclient import TestClient
from servidor.main import app
import os

client = TestClient(app)

# Test upload y download de archivo permitido
def test_upload_download_archivo():
    archivo = ("test.txt", b"contenido de prueba", "text/plain")
    resp = client.post("/api/v1/archivo/upload/sesiondemo/peer1", files={"file": archivo})
    assert resp.status_code == 200
    nombre = resp.json()["filename"]
    # Descargar
    resp2 = client.get(f"/api/v1/archivo/download/{nombre}")
    assert resp2.status_code == 200
    assert resp2.content == b"contenido de prueba"

# Test rechazo de archivo no permitido
def test_upload_archivo_no_permitido():
    archivo = ("malware.exe", b"binario", "application/octet-stream")
    resp = client.post("/api/v1/archivo/upload/sesiondemo/peer1", files={"file": archivo})
    assert resp.status_code == 400
    assert "no permitido" in resp.json()["detail"]

# Test rechazo de archivo demasiado grande
def test_upload_archivo_grande():
    archivo = ("grande.pdf", b"0" * (11 * 1024 * 1024), "application/pdf")
    resp = client.post("/api/v1/archivo/upload/sesiondemo/peer1", files={"file": archivo})
    assert resp.status_code == 400
    assert "demasiado grande" in resp.json()["detail"]
