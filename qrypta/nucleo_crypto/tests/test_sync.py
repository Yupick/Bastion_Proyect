import pytest

from nucleo_crypto.sync import (
    ErrorDispositivoRevocado,
    ErrorVinculoSincronizacion,
    crear_estado_sincronizacion,
    descifrar_estado_inicial,
    firmar_vinculo_dispositivo,
    registrar_estado_lectura,
    registrar_mensaje,
    revocar_dispositivo,
    sincronizar_dispositivo,
    vincular_dispositivo,
)


MAESTRO = "maestro-001"
DISPOSITIVO_1 = "dispositivo-001"
DISPOSITIVO_2 = "dispositivo-002"
DISPOSITIVO_3 = "dispositivo-003"


def _crear_estado() -> object:
    return crear_estado_sincronizacion(
        MAESTRO,
        estado_inicial={
            "ultimo_mensaje": "mensaje-001",
            "sesion_activa": "true",
            "contador": "12",
        },
        secreto_maestro=b"x" * 32,
    )


def test_vincular_y_descifrar_estado_inicial():
    estado = _crear_estado()
    firma = firmar_vinculo_dispositivo(estado, DISPOSITIVO_1)

    paquete = vincular_dispositivo(estado, DISPOSITIVO_1, firma)
    estado_recuperado = descifrar_estado_inicial(estado, DISPOSITIVO_1, paquete)

    assert estado_recuperado["ultimo_mensaje"] == "mensaje-001"
    assert estado_recuperado["sesion_activa"] == "true"
    assert estado_recuperado["contador"] == "12"


def test_vinculo_invalido_rechazado():
    estado = _crear_estado()

    with pytest.raises(ErrorVinculoSincronizacion):
        vincular_dispositivo(estado, DISPOSITIVO_1, "firma-invalida")


def test_sincroniza_eventos_y_lecturas():
    estado = _crear_estado()
    firma = firmar_vinculo_dispositivo(estado, DISPOSITIVO_1)
    vincular_dispositivo(estado, DISPOSITIVO_1, firma)

    registrar_mensaje(estado, DISPOSITIVO_1, "msg-1")
    registrar_estado_lectura(estado, DISPOSITIVO_1, "msg-1")
    registrar_mensaje(estado, DISPOSITIVO_1, "msg-2", leido=True)

    eventos = sincronizar_dispositivo(estado, DISPOSITIVO_1, ultimo_seq=0)

    assert [evento.tipo for evento in eventos] == ["vinculo", "mensaje", "lectura", "mensaje"]
    assert eventos[1].datos["mensaje_id"] == "msg-1"
    assert eventos[2].datos["mensaje_id"] == "msg-1"
    assert eventos[3].datos["leido"] == "true"


def test_revocar_dispositivo_bloquea_sincronizacion():
    estado = _crear_estado()
    firma = firmar_vinculo_dispositivo(estado, DISPOSITIVO_1)
    vincular_dispositivo(estado, DISPOSITIVO_1, firma)

    revocar_dispositivo(estado, DISPOSITIVO_1, MAESTRO)

    with pytest.raises(ErrorDispositivoRevocado):
        sincronizar_dispositivo(estado, DISPOSITIVO_1)

    firma_nueva = firmar_vinculo_dispositivo(estado, DISPOSITIVO_2)
    paquete = vincular_dispositivo(estado, DISPOSITIVO_2, firma_nueva)
    estado_recuperado = descifrar_estado_inicial(estado, DISPOSITIVO_2, paquete)
    assert estado_recuperado["sesion_activa"] == "true"


def test_solo_maestro_puede_revocar():
    estado = _crear_estado()
    firma = firmar_vinculo_dispositivo(estado, DISPOSITIVO_1)
    vincular_dispositivo(estado, DISPOSITIVO_1, firma)

    with pytest.raises(PermissionError):
        revocar_dispositivo(estado, DISPOSITIVO_1, DISPOSITIVO_3)
