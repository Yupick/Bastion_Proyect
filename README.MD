# Sistema de Mensajería Híbrido con PQC

Este sistema permite comunicación segura, privada y auditable usando criptografía poscuántica (Kyber + Dilithium), alias opcionales y auditoría pública. No requiere servidores que almacenen identidades ni contenido.

## Características
- Claves generadas localmente (Kyber + Dilithium)
- Alias opcionales firmados
- Verificación de mensajes por firma digital
- Lista de contactos local
- Backup cifrado con AES-256
- Auditoría pública verificable
- TUI de configuración y administración (Textual)

## Administración y TUI

- Ejecuta la TUI de configuración:
  ```bash
  python -m servidor.tui.configuracion
  ```
- El panel permite editar variables del servidor y ver logs de auditoría.
- Los cambios se guardan en `.env` y se aplican al reiniciar el servidor.

