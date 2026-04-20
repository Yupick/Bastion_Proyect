# Qrypta

Sistema de mensajeria hibrido poscuantico con privacidad radical y auditoria verificable.

## Estructura
- servidor/: API FastAPI, TUI y dashboard
- servidor/dashboard_admin_web/: panel admin web (React + TypeScript)
- servidor/admin_consola/: entrypoint de consola de administracion
- nucleo_crypto/: primitivas y logica de seguridad
- cliente_movil/: Flutter (Android/iOS)
- cliente_web/: React + TypeScript
- cliente_escritorio/: Tauri v2 (Windows/Linux)

## GitFlow
- main: estable
- develop: integracion
- feature/*, release/*, hotfix/*
