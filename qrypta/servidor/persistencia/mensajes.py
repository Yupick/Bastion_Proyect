"""Persistencia de mensajes pendientes.

Proposito: almacenar y recuperar mensajes pendientes usando SQLite/PostgreSQL.
Autor: Qrypta Team
Fecha: 2026-03-30
"""

import sqlite3
import time
from typing import Any, List, Optional

DB_PATH = "servidor_mensajes.db"

class MensajePendiente:
    def __init__(self, peer_id: str, payload: str, timestamp: float, ttl: int = 86400):
        self.peer_id = peer_id
        self.payload = payload
        self.timestamp = timestamp
        self.ttl = ttl

    def to_tuple(self):
        return (self.peer_id, self.payload, self.timestamp, self.ttl)


def init_db(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS mensajes_pendientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peer_id TEXT NOT NULL,
            payload TEXT NOT NULL,
            timestamp REAL NOT NULL,
            ttl INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_peer_id ON mensajes_pendientes(peer_id);
        CREATE INDEX IF NOT EXISTS idx_timestamp ON mensajes_pendientes(timestamp);
        """
    )
    conn.commit()
    conn.close()


def guardar_mensaje(mensaje: MensajePendiente, db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "INSERT INTO mensajes_pendientes (peer_id, payload, timestamp, ttl) VALUES (?, ?, ?, ?)",
        mensaje.to_tuple(),
    )
    conn.commit()
    conn.close()


def obtener_mensajes(peer_id: str, db_path: str = DB_PATH) -> List[MensajePendiente]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "SELECT peer_id, payload, timestamp, ttl FROM mensajes_pendientes WHERE peer_id = ? ORDER BY timestamp ASC",
        (peer_id,),
    )
    rows = c.fetchall()
    mensajes = [MensajePendiente(*row) for row in rows]
    conn.close()
    return mensajes


def eliminar_mensajes(peer_id: str, db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM mensajes_pendientes WHERE peer_id = ?", (peer_id,))
    conn.commit()
    conn.close()


def limpiar_expirados(db_path: str = DB_PATH):
    ahora = time.time()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "DELETE FROM mensajes_pendientes WHERE timestamp + ttl < ?",
        (ahora,)
    )
    conn.commit()
    conn.close()
