"""Gestión de sesiones E2E y grupos para Qrypta."""
from typing import Dict, List, Optional
from uuid import uuid4
from datetime import datetime, timedelta

class Sesion:
    def __init__(self, tipo: str, miembros: List[str], ttl: int = 3600):
        self.id = str(uuid4())
        self.tipo = tipo  # '1a1' o 'grupo'
        self.miembros = miembros
        self.creado = datetime.utcnow()
        self.expira = self.creado + timedelta(seconds=ttl)
        self.mensajes = []  # historial en memoria
        self.archivos = []  # metadatos de archivos

    def agregar_mensaje(self, mensaje: dict):
        self.mensajes.append(mensaje)

    def agregar_archivo(self, archivo: dict):
        self.archivos.append(archivo)

    def es_valida(self):
        return datetime.utcnow() < self.expira

class GestorSesiones:
    def __init__(self):
        self.sesiones: Dict[str, Sesion] = {}

    def crear_sesion(self, tipo: str, miembros: List[str], ttl: int = 3600) -> Sesion:
        sesion = Sesion(tipo, miembros, ttl)
        self.sesiones[sesion.id] = sesion
        return sesion

    def obtener_sesion(self, sesion_id: str) -> Optional[Sesion]:
        sesion = self.sesiones.get(sesion_id)
        if sesion and sesion.es_valida():
            return sesion
        return None

    def limpiar_expiradas(self):
        ahora = datetime.utcnow()
        self.sesiones = {k: v for k, v in self.sesiones.items() if v.expira > ahora}
