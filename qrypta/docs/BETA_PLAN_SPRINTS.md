# Plan de Fases y Sprints para Llegar a Beta

Fecha: 2026-05-25

## Objetivo
Llegar a una beta cerrada del sistema con un núcleo funcional, criptografía verificable, sincronización básica entre dispositivos, notificaciones push, grupos, y una cadena CI/CD reproducible.

## Criterio de Beta
La beta puede abrirse cuando se cumpla todo esto:
- `qrypta/nucleo_crypto/tests` pasa en CI con `oqs` disponible.
- El servidor arranca en local y en staging con scripts reproducibles.
- Push, DHT, grupos y WebSockets tienen rutas funcionales y pruebas mínimas.
- Al menos un cliente web y un cliente móvil compilan y ejecutan smoke tests.
- Existe un flujo de release y rollback documentado.

## Principios de ejecución
- Cada sprint debe entregar algo verificable, no solo documentación.
- Primero se estabiliza la base crítica: dependencias nativas, CI, staging y pruebas.
- Después se completa el flujo de producto: push, grupos, sync y clientes.
- Cada fase termina con una validación automática o manual clara.

## Fase 1 - Estabilización de la base
### Sprint 1 - Entorno reproducible y CI
Duración sugerida: 1 semana

Objetivos:
- Hacer reproducible el entorno de desarrollo.
- Hacer que CI instale `oqs` o un equivalente viable en Ubuntu.
- Consolidar dependencias de desarrollo.

Entregables:
- `requirements-dev.txt` operativo.
- `devcontainer` funcional.
- Workflows de `ci-nucleo` y `ci-servidor` con instalación de dependencias nativas.
- Documentación de desbloqueo de entorno actualizada.

Criterio de salida:
- `pytest qrypta/nucleo_crypto/tests -q` corre en CI o queda claramente segmentado por skips controlados.

### Sprint 2 - Staging y servidor base
Duración sugerida: 1 semana

Objetivos:
- Asegurar un servidor de staging reproducible.
- Cerrar lo mínimo de REST, auditoría y colas.

Entregables:
- `Dockerfile` y `docker-compose` revisados para servidor.
- Script de despliegue local/staging.
- Endpoints REST base validados.
- Logs y métricas mínimas accesibles.

Criterio de salida:
- El servidor arranca con un solo comando en local y en staging.

## Fase 2 - Núcleo de seguridad
### Sprint 3 - E2E y autenticación real
Duración sugerida: 1 semana

Objetivos:
- Completar la autenticación real en WebSockets.
- Reforzar handshake y verificación de firmas.

Entregables:
- Verificación de firma Dilithium implementada en WS.
- Validación de timestamps y anti-replay mejorada.
- Tests de sesión y WebSocket más estrictos.

Criterio de salida:
- Un cliente no autenticado no puede mantener sesión WS.

### Sprint 4 - Sync de dispositivos
Duración sugerida: 1 semana

Objetivos:
- Introducir sincronización multi-dispositivo mínima.
- Resolver el ciclo de alta, transferencia inicial y revocación.

Entregables:
- Módulo `sync` real en `nucleo_crypto`.
- API para vincular dispositivo, transferir estado inicial y revocar.
- Tests de regresión para sincronización.

Criterio de salida:
- Un segundo dispositivo puede unirse y sincronizar un estado inicial seguro.

## Fase 3 - Funcionalidades de mensajería
### Sprint 5 - Push y presencia
Duración sugerida: 1 semana

Objetivos:
- Pasar de simulación a implementación funcional de push.
- Dejar la privacidad claramente definida.

Entregables:
- Registro y baja de tokens por dispositivo.
- Envío de aviso de mensaje pendiente sin contenido sensible.
- Integración técnica con FCM/APNs o un adaptador simulable en beta.
- Tests de presencia y notificación.

Criterio de salida:
- Un peer desconectado recibe aviso sin contenido del mensaje.

### Sprint 6 - Grupos y rotación de clave
Duración sugerida: 1 semana

Objetivos:
- Formalizar la gestión de grupos.
- Hacer que la rotación de clave sea parte del flujo normal.

Entregables:
- Alta/baja de miembros con firma del admin.
- Rotación de clave de grupo al expulsar miembros.
- Persistencia o almacenamiento temporal controlado.
- Tests de grupo y permisos.

Criterio de salida:
- Un miembro expulsado no debe seguir pudiendo leer mensajes nuevos del grupo.

## Fase 4 - Descubrimiento y clientes
### Sprint 7 - DHT y descubrimiento
Duración sugerida: 1 semana

Objetivos:
- Convertir la DHT en algo más sólido que un mapa local simplificado.
- Asegurar publicación, búsqueda y renovación con firma.

Entregables:
- Publicación de peer con endpoint firmado.
- Búsqueda por `peer_id`.
- Renovación y expiración con TTL real.
- Tests de expiración y renovación.

Criterio de salida:
- Un peer publicado se puede encontrar y expira correctamente.

### Sprint 8 - Clientes beta
Duración sugerida: 1 semana

Objetivos:
- Cerrar la capa mínima de cliente web y cliente móvil para beta.
- Confirmar que el cliente de escritorio no bloquea el release aunque le falte el updater.

Entregables:
- Web con smoke tests verdes.
- Mobile con smoke tests/análisis verdes.
- Escritorio con build estable y pruebas mínimas.
- Ajustes de interfaz para flujos beta críticos.

Criterio de salida:
- Se pueden realizar mensajes, ver estado y validar presencia desde al menos un cliente web y uno móvil.

## Fase 5 - Cierre beta
### Sprint 9 - Hardening y release
Duración sugerida: 1 semana

Objetivos:
- Reducir riesgos antes de abrir beta cerrada.
- Estabilizar documentación, release y rollback.

Entregables:
- Checklist final de beta.
- Tag de release candidato.
- Instrucciones de despliegue, rollback y soporte.
- Registro de bugs conocidos y límites del beta.

Criterio de salida:
- Se puede entregar una beta cerrada con comportamiento predecible y plan de soporte.

## Mapa de fases del plan maestro a sprints
- Fase 9 -> Sprint 7
- Fase 10 -> Sprint 5
- Fase 11 -> Sprint 6
- Fase 12 -> Sprint 4
- Fase 13 -> Sprint 8
- Fase 14 -> Sprint 1, Sprint 2 y Sprint 9

## Riesgos principales
- `oqs` puede requerir dependencias nativas no disponibles por defecto.
- Flutter y Tauri dependen de toolchains externas que no están listas en cualquier máquina.
- FCM/APNs pueden requerir secretos y configuración externa antes de validar push real.
- El alcance de beta debe limitarse: no intentar cerrar todo el roadmap completo antes de liberar.

## Recomendación práctica
Si el objetivo es beta en el menor tiempo razonable, el orden correcto es:
1. Sprint 1 y 2 para estabilizar base.
2. Sprint 3 y 4 para seguridad y sync.
3. Sprint 5, 6 y 7 para completar las capacidades diferenciales.
4. Sprint 8 y 9 para validación final y release.
