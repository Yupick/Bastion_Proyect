# Plan de Trabajo Siguiente — Qrypta

Generado: 2026-05-25

Resumen rápido:
- Estado actual: la rama `fix/persistencia-scripts` contiene correcciones en persistencia y scripts de ops; PR abierto: https://github.com/Yupick/Bastion_Proyect/pull/12
- Tests Python del servidor pasan; ejecución completa de `pytest` mostró fallos en `nucleo_crypto` por falta de la dependencia nativa `liboqs`.

Bloqueantes detectados:
- Dependencia nativa `liboqs` (bindings Python `oqs`) no disponible en entorno local/CI → varios tests de `nucleo_crypto` fallan.
- Entorno de build para Tauri (Rust/cargo) y Flutter (Android SDK) no presente en esta sesión (ver `GUIA_DESBLOQUEO_ENTORNO.md`).

Objetivos prioritarios (próximas 4 semanas):
1. Asegurar reproducibilidad CI y entorno de desarrollo (2-3 días)
   - Añadir instrucciones y/o scripts para instalar `oqs` en GitHub Actions (ci-nucleo, ci-servidor).
   - Crear `requirements-dev.txt` / `devcontainer` o actualizar `GUIA_DESBLOQUEO_ENTORNO.md` para pasos de instalación de `liboqs` y dependencias nativas.
   - Validar en un runner Ubuntu que `pip install oqs` o apt/pkgs instalan correctamente antes de ejecutar tests.

2. Completar y estabilizar server + tests (3-5 días)
   - Revisar tests de `nucleo_crypto` que no manejan ausencia de `oqs` y decidir: instalar `oqs` en CI o marcar tests para skip condicional.
   - Añadir `oqs` a los requisitos de CI o a un job dedicado (opción: `pip install oqs` en workflow antes de pytest).
   - Actualizar `qrypta/servidor/requirements.txt` o crear `qrypta/servidor/requirements-dev.txt` con `pytest-asyncio`, `oqs` (si procede) y herramientas de desarrollo.

3. Desbloquear toolchains para clientes (Tauri / Flutter) (4-7 días)
   - Documentar pasos manuales para instalar Rust/cargo y Android SDK en `GUIA_DESBLOQUEO_ENTORNO.md` (ya existe) y añadir alternativas automatizadas para CI.
   - Preparar contenedores Docker o devcontainers con Rust + Android SDK para reproducibilidad.

4. Continuar roadmap funcional (Fase 10–12 priorizadas) (sprint por fase, 1-2 semanas por fase)
   - Fase 10 (Push): implementar registro de tokens, endpoints y pruebas E2E (FCM/APNs). Dependencia: CI mobile o staging con credenciales.
   - Fase 11 (Grupos): diseñar esquema de claves de grupo, APIs y tests de integración E2E.
   - Fase 12 (Sync): incluir tests de sincronización multi-dispositivo y validación de ratchet.

Tareas inmediatas que propongo ejecutar ahora (elige cuales quieres que haga yo):
- [ ] Actualizar workflows (`.github/workflows/ci-nucleo.yml` y `ci-servidor.yml`) para intentar instalar `oqs` antes de `pytest`.
- [x] Añadir `pytest-asyncio` a `qrypta/servidor/requirements.txt` (ya realizado en la rama `fix/persistencia-scripts`).
- [x] Crear PR con los cambios (PR #12).
- [ ] Añadir `requirements-dev.txt` y un `devcontainer` (Dockerfile) para desarrolladores.
- [ ] Preparar Dockerfile de servidor (si aún falta) que incluya pasos opcionales para `oqs`.

Estimaciones y orden de prioridad:
- Prioridad Alta: CI reproducible (liboqs, tests), doc de desbloqueo, PR/merge a `develop`.
- Prioridad Media: Devcontainers/Docker, builds Tauri/Flutter en CI.
- Prioridad Baja: optimizaciones UI, performance y despliegues (después de estabilizar core).

Entradas pendientes/recursos necesarios:
- Acceso a runners CI con permisos de instalación (GitHub Actions es suficiente si añadimos pasos apt/pip).
- Posible necesidad de credenciales para servicios (FCM/APNs) para pruebas push.
- Tiempo para compilar/validar liboqs en runners (puede requerir CMake, OpenSSL, etc.).

Propuesta inmediata de PRs adicionales:
1. `ci/oqs-install` — modifica `ci-nucleo.yml` y `ci-servidor.yml` para intentar `pip install oqs` o instalar paquete del sistema antes de tests.
2. `dev/devcontainer` — añade `devcontainer.json` + Dockerfile con Python3.12, Rust, Android SDK (opcional) para onboarding.

Si estás de acuerdo, aplico la siguiente orden: 1) actualizar workflows CI para probar instalación `oqs`; 2) añadir `requirements-dev.txt`; 3) abrir PRs separados para cada cambio.

---

Autor: Equipo automatizado (acciones realizadas: añadir `pytest-asyncio`, correcciones ws, commits y PR #12)
