"""Intercambio de claves publicas.

Proposito: generar y leer QR/codigos de contacto.
Autor: Qrypta Team
Fecha: 2026-03-29
Ejemplo de uso: generarQr(...)
"""

from __future__ import annotations

import base64
import io
import json

from nucleo_crypto.crypto.keygen import DependenciaCriptograficaError

PREFIJO_CODIGO = "qrypta://"

try:
    import qrcode
except ImportError:  # pragma: no cover - depende del entorno.
    qrcode = None


def generarCodigoTexto(clavePublica: dict[str, object]) -> str:
    """Serializa identidad publica en un codigo compacto."""
    payload = json.dumps(clavePublica, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    token = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    return f"{PREFIJO_CODIGO}{token}"


def decodificarCodigo(codigo: str) -> dict[str, object]:
    """Decodifica un codigo qrypta:// a diccionario de identidad publica."""
    if not codigo.startswith(PREFIJO_CODIGO):
        raise ValueError("Codigo invalido: prefijo no reconocido.")

    token = codigo[len(PREFIJO_CODIGO) :]
    padding = "=" * ((4 - (len(token) % 4)) % 4)
    payload = base64.urlsafe_b64decode((token + padding).encode("ascii"))
    return json.loads(payload.decode("utf-8"))


def generarQr(clavePublica: dict[str, object]) -> bytes:
    """Genera una imagen PNG con un codigo QR de los datos publicos."""
    if qrcode is None:
        raise DependenciaCriptograficaError(
            "La dependencia 'qrcode' no esta disponible. Instala 'qrcode[pil]'."
        )

    codigo = generarCodigoTexto(clavePublica)
    imagen = qrcode.make(codigo)
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()
