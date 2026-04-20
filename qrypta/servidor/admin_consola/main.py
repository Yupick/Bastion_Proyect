"""Entrypoint de consola de administracion.

Proposito: exponer una ruta estable para lanzar la TUI administrativa.
Autor: Qrypta Team
Fecha: 2026-04-19
Ejemplo de uso: python -m servidor.admin_consola.main
"""

from servidor.tui.configuracion import main


if __name__ == "__main__":
    main()
