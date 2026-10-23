"""Configuracion global de pytest para tests del servidor."""

import os

# Habilitar modo test para saltar verificacion de firmas (sin oqs)
os.environ["QRYPTA_TEST_MODE"] = "true"
os.environ["QRYPTA_PUSH_STUB"] = "true"