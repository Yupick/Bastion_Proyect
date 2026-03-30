"""Gestión y validación de archivos para Qrypta."""
from typing import List
from pathlib import Path

TIPOS_PERMITIDOS = [
    ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".docx", ".xlsx", ".pptx", ".zip", ".txt"
]
TAM_MAX_MB = 10
TAM_MAX_BYTES = TAM_MAX_MB * 1024 * 1024

class ArchivoInvalido(Exception):
    pass

def validar_archivo(nombre: str, tam: int):
    ext = Path(nombre).suffix.lower()
    if ext not in TIPOS_PERMITIDOS:
        raise ArchivoInvalido(f"Tipo de archivo no permitido: {ext}")
    if tam > TAM_MAX_BYTES:
        raise ArchivoInvalido(f"Archivo demasiado grande: {tam} bytes (máx {TAM_MAX_MB} MB)")
    return True
