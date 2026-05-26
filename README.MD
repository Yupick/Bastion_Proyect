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

## Onboarding rápido (desarrollo)

### 1) Preparar entorno local

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r qrypta/servidor/requirements-dev.txt
```

### 2) Ejecutar pruebas

```bash
pytest -q qrypta/servidor/tests
pytest -q qrypta/nucleo_crypto/tests
```

Nota: si `oqs` no está disponible, algunos tests criptográficos se omiten automáticamente.

### 3) Levantar servidor local

```bash
bash scripts/server_ctl.sh start
bash scripts/server_ctl.sh status
bash scripts/server_ctl.sh logs
```

### 4) Usar Dev Container en VS Code

- Abrir el comando: `Dev Containers: Reopen in Container`.
- El contenedor instala dependencias con `requirements-dev.txt` al crearse.

## Beta de clientes (gate de preparación)

- Ejecuta el gate unificado:
  `scripts/beta_clients_ready.sh`
- El script valida:
  - Cliente web: tests + build
  - Cliente escritorio: tests + build
  - Cliente móvil: flutter test
- Genera reporte en:
  - `qrypta/docs/BETA_CLIENTS_READINESS.md`

