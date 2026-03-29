from nucleo_crypto.compartir.qr import decodificarCodigo, generarCodigoTexto


def test_generar_y_decodificar_codigo_texto():
    datosPublicos = {
        "peerId": "a" * 64,
        "pubkeyKyberB64": "a2V5",
        "pubkeyDilithiumB64": "cHVi",
    }

    codigo = generarCodigoTexto(datosPublicos)
    recuperado = decodificarCodigo(codigo)

    assert recuperado == datosPublicos
