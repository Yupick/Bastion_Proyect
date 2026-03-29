from pathlib import Path

from servidor.tui import configuracion


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
