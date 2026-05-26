"""Configuracion de tests del nucleo criptografico."""

from __future__ import annotations

import pytest

from nucleo_crypto.crypto import keygen


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Hace skip de tests marcados si oqs no esta disponible en el entorno."""
    if keygen.oqs is not None:
        return

    skip_oqs = pytest.mark.skip(reason="liboqs-python no disponible en el entorno de pruebas")
    for item in items:
        if "requires_oqs" in item.keywords:
            item.add_marker(skip_oqs)
