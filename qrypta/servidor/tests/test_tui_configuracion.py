from pathlib import Path

from servidor.tui import configuracion
from servidor.tui.configuracion import (
    banearUsuario,
    desbanearUsuario,
    ejecutarSelectSeguro,
    exportarCsv,
    exportarJson,
    listarTablas,
    listarUsuarios,
)


def test_guardar_y_cargar_env_local(tmp_path, monkeypatch):
    rutaTemporal = tmp_path / ".env"
    monkeypatch.setattr(configuracion, "rutaEnvLocal", lambda: rutaTemporal)

    configuracion.guardarEnvLocal({"HOST": "127.0.0.1", "PUERTO": "8001"})
    cargado = configuracion.cargarEnvLocal()

    assert cargado["HOST"] == "127.0.0.1"
    assert cargado["PUERTO"] == "8001"


def test_ultimas_lineas(tmp_path):
    ruta = tmp_path / "auditoria.jsonl"
    ruta.write_text("\n".join(str(i) for i in range(100)), encoding="utf-8")

    salida = configuracion.ultimasLineas(ruta, limite=5)
    assert salida == ["95", "96", "97", "98", "99"]


def test_ultimas_lineas_archivo_inexistente(tmp_path):
    salida = configuracion.ultimasLineas(tmp_path / "no-existe.log")
    assert salida == []


# ---------------------------------------------------------------------------
# Gestión de usuarios (AdminTUI.2)
# ---------------------------------------------------------------------------

def test_banear_y_listar_usuario(tmp_path, monkeypatch):
    monkeypatch.setattr(configuracion, "_USUARIOS_FILE", tmp_path / "usuarios_ban.json")
    resultado = banearUsuario("peer-abc", "spam")
    assert resultado is True
    usuarios = listarUsuarios()
    assert any(u["id"] == "peer-abc" and u["estado"] == "baneado" for u in usuarios)


def test_desbanear_usuario_existente(tmp_path, monkeypatch):
    monkeypatch.setattr(configuracion, "_USUARIOS_FILE", tmp_path / "usuarios_ban.json")
    banearUsuario("peer-xyz")
    ok = desbanearUsuario("peer-xyz")
    assert ok is True
    assert not any(u["id"] == "peer-xyz" for u in listarUsuarios())


def test_desbanear_usuario_inexistente(tmp_path, monkeypatch):
    monkeypatch.setattr(configuracion, "_USUARIOS_FILE", tmp_path / "usuarios_ban.json")
    ok = desbanearUsuario("no-existe")
    assert ok is False


def test_banear_id_vacio(tmp_path, monkeypatch):
    monkeypatch.setattr(configuracion, "_USUARIOS_FILE", tmp_path / "usuarios_ban.json")
    assert banearUsuario("") is False
    assert banearUsuario("   ") is False


# ---------------------------------------------------------------------------
# SQL Browser (AdminTUI.3)
# ---------------------------------------------------------------------------

import sqlite3


def _crearDbTest(tmp_path: Path) -> Path:
    """Crea una base SQLite de prueba con datos mínimos."""
    db = tmp_path / "test.db"
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE mensajes (id INTEGER PRIMARY KEY, texto TEXT)")
    conn.execute("INSERT INTO mensajes VALUES (1, 'hola')")
    conn.execute("INSERT INTO mensajes VALUES (2, 'mundo')")
    conn.commit()
    conn.close()
    return db


def test_listar_tablas(tmp_path):
    db = _crearDbTest(tmp_path)
    tablas = listarTablas(db)
    assert "mensajes" in tablas


def test_ejecutar_select_seguro(tmp_path):
    db = _crearDbTest(tmp_path)
    columnas, filas = ejecutarSelectSeguro("SELECT * FROM mensajes", db)
    assert "id" in columnas
    assert len(filas) == 2


def test_select_rechaza_no_select(tmp_path):
    db = _crearDbTest(tmp_path)
    import pytest
    with pytest.raises(ValueError, match="SELECT"):
        ejecutarSelectSeguro("DROP TABLE mensajes", db)


def test_select_rechaza_insert(tmp_path):
    db = _crearDbTest(tmp_path)
    import pytest
    with pytest.raises(ValueError):
        ejecutarSelectSeguro("INSERT INTO mensajes VALUES (3, 'inyeccion')", db)


def test_exportar_csv(tmp_path):
    db = _crearDbTest(tmp_path)
    csv_str = exportarCsv("mensajes", db)
    assert "id" in csv_str
    assert "hola" in csv_str
    assert "mundo" in csv_str


def test_exportar_csv_tabla_invalida(tmp_path):
    db = _crearDbTest(tmp_path)
    import pytest
    with pytest.raises(ValueError, match="Tabla no encontrada"):
        exportarCsv("no_existe", db)


def test_exportar_json(tmp_path):
    db = _crearDbTest(tmp_path)
    result = exportarJson("mensajes", db)
    datos = __import__("json").loads(result)
    assert isinstance(datos, list)
    assert datos[0]["texto"] == "hola"


def test_exportar_json_tabla_invalida(tmp_path):
    db = _crearDbTest(tmp_path)
    import pytest
    with pytest.raises(ValueError, match="Tabla no encontrada"):
        exportarJson("wrong_table", db)


def test_listar_tablas_db_inexistente(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        listarTablas(tmp_path / "no_existe.db")
