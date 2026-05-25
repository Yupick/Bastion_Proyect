# Informe de Preparación para Beta Test — Qrypta

Fecha: 2026-05-25

Resumen ejecutivo
------------------
El repositorio está funcional para desarrollo local del servidor y de clientes web. Se han corregido varios fallos del backend, los tests del servidor pasan y hay un plan de trabajo para estabilizar dependencias nativas (liboqs) y toolchains (Rust/Android) necesarios para builds de Tauri y Flutter.

Estado actual (resumen)
- Branch principal para integración: `develop` (actualizado).
- Correcciones aplicadas y PR #12 mergeado (persistencia y scripts de ops).
- Servidor local arrancable con `bash scripts/server_ctl.sh start` y tests de `qrypta/servidor/tests` en verde.
- `pytest-asyncio` añadido a `qrypta/servidor/requirements.txt` y `qrypta/servidor/requirements-dev.txt` creado.
- CI actualizado (propuesta) para intentar instalar `oqs` antes de `pytest`.
- Devcontainer básico añadido en `.devcontainer/` para onboarding.

Faltantes críticos para lanzar un Beta Test
----------------------------------------
1. Dependencias nativas PQC (liboqs / Python binding `oqs`)
   - Estado: no disponible en runners locales por defecto; algunos tests fallaron hasta instalarlo.
   - Impacto: tests del `nucleo_crypto` y funcionalidades E2E dependen de liboqs; sin ella no podemos verificar criptografía real.
   - Acción requerida: configurar CI para instalar `oqs` o añadir un job que construya liboqs en runner; documentar pasos en `GUIA_DESBLOQUEO_ENTORNO.md`.

2. Entornos de build para clientes nativos
   - Rust/Cargo para Tauri (cliente escritorio).
   - Android SDK + Java toolchain para Flutter (cliente móvil).
   - Impacto: no se pueden generar binarios para testers ni realizar E2E móviles.
   - Acción requerida: provisionar runners o contenedores (devcontainer/Docker) con Rust y Android SDK; añadir workflows de build.

3. Pipelines CI/CD completos y reproducibles
   - Estado: workflows por componente existen; falta garantizar `oqs` y toolchains en CI.
   - Acción requerida: añadir pasos de instalación de dependencias nativas y pruebas E2E en CI; asegurar secretos (FCM/APNs) para pruebas push.

4. Entorno de staging y despliegue
   - Necesario: una instancia staging del servidor (Docker o VM) con métricas y logs accesibles para testers.
   - Acción requerida: crear `docker-compose` para staging y script de despliegue, o usar infra cloud para staging.

5. Documentación y onboarding de testers
   - Incluir guías rápidas: cómo instalar el cliente web, cómo generar claves, cómo reportar bugs.
   - Preparar checklist de pruebas para testers (registro, enviar/recibir mensajes, adjuntos, restauración de backup, revocación de dispositivos).

Checklist mínimo para comenzar Beta
----------------------------------
- [ ] CI instala y verifica `oqs` en Ubuntu runners (o tests marcados para skip).
- [ ] Devcontainer listo con Python, Node y Rust (construible por desarrolladores).
- [ ] Builds básicos del cliente web desplegados en entorno staging (Vite build + host estático).
- [ ] Servidor desplegable en Docker-compose para staging con logging/metrics.
- [ ] Guía de testers creada y publicada en `docs/`.
- [ ] Test plan básico (smoke tests + rutas críticas) y registro de issues activo.

Recomendaciones inmediatas (acciones en 1–3 días)
-----------------------------------------------
1. Implementar en CI el paso para instalar `oqs` (ya propuesto en `ci-nucleo.yml` y `ci-servidor.yml`).
2. Crear un `devcontainer` completo (ya añadido un template) y asegurar que construye en local.
3. Provisionar un staging con `docker-compose` para el servidor y desplegar cliente web estático.
4. Preparar el paquete de onboarding para testers: instrucciones, credenciales de acceso (si aplica) y canales de reporte.

Conclusión
----------
Con los cambios aplicados y las tareas críticas completadas (en particular la instalación de `oqs` en CI y la provisión de toolchains para Tauri/Flutter), el proyecto estará listo para iniciar un beta test cerrado. Recomiendo priorizar la configuración CI y el staging en los próximos 2–4 días.
