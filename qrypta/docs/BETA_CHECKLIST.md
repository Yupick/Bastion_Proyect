# Checklist Final Beta - Qrypta

_Fecha: 2026-05-25 | Versión candidata: v0.1.0-beta_

---

## Criterios de Aceptación Beta (desde PLAN.md)

| # | Criterio | Estado | Evidencia |
|---|----------|--------|-----------|
| 1 | `qrypta/nucleo_crypto/tests` pasa en CI con `oqs` disponible | ⬜ | CI nucleo-oqs (skipped si no oqs) |
| 2 | Servidor arranca en local y staging con scripts reproducibles | ⬜ | `server_ctl.sh`, `docker-compose.staging.yml` |
| 3 | Push, DHT, grupos y WebSockets tienen rutas funcionales y pruebas mínimas | ⬜ | Tests integración + docs |
| 4 | Al menos un cliente web y uno móvil compilan y ejecutan smoke tests | ⬜ | `beta_clients_ready.sh` PASS |
| 5 | Existe flujo de release y rollback documentado | ⬜ | `DEPLOYMENT_GUIDE.md` |

---

## Validación Técnica

### Núcleo Criptográfico
- [ ] Tests unitarios PASS (core + oqs skipped)
- [ ] Generación claves Kyber768 + Dilithium3
- [ ] KEM encapsular/desencapsular
- [ ] Firma/verificación Dilithium
- [ ] AES-256-GCM cifrado/descifrado
- [ ] Argon2id KDF
- [ ] BIP-39 mnemonic 24 palabras
- [ ] Backup export/import con checksum + firma

### Servidor
- [ ] REST API: health, mensajes, contactos, auditoría
- [ ] WebSocket autenticado (firma Dilithium)
- [ ] Rate limiting funcional
- [ ] Auditoría sin PII
- [ ] Docker build + healthcheck PASS
- [ ] docker-compose.staging.yml deploy PASS
- [ ] Logs estructurados + rotación
- [ ] Métricas Prometheus expuestas

### Push & Presencia
- [ ] Registro token dispositivo
- [ ] Envío aviso "mensaje pendiente" (sin contenido)
- [ ] Baja token
- [ ] Presence online/offline

### Grupos E2E
- [ ] Crear sala
- [ ] Alta/baja miembros (firma admin)
- [ ] Rotación clave al expulsar
- [ ] Envío/recv mensajes grupo
- [ ] Miembro expulsado no lee nuevos

### Sync Multi-dispositivo
- [ ] Vincular dispositivo (firma maestro)
- [ ] Transferencia estado inicial cifrada
- [ ] Sync mensajes + lectura
- [ ] Revocar dispositivo comprometido

### DHT Descubrimiento
- [ ] Publicar peer con endpoint firmado
- [ ] Buscar por peer_id
- [ ] TTL + renovación
- [ ] Expiración correcta

---

## Validación Clientes

### Cliente Web (React + TS)
- [ ] `npm run test:run` PASS
- [ ] `npm run build` PASS
- [ ] Registro local + BIP-39
- [ ] Chat E2E funcional
- [ ] Contactos + presencia
- [ ] Grupos UI
- [ ] Backup/restore UI
- [ ] PWA: install + offline read

### Cliente Móvil (Flutter)
- [ ] `flutter test` PASS
- [ ] `flutter build apk` PASS (Android)
- [ ] Registro local + BIP-39
- [ ] Chat E2E funcional
- [ ] Contactos + presencia
- [ ] Grupos UI
- [ ] Backup/restore UI
- [ ] Push notifications (FCM)

### Cliente Escritorio (Tauri)
- [ ] `npm run test:run` PASS
- [ ] `npm run build` PASS
- [ ] `cargo tauri build` PASS (Windows/Linux)
- [ ] Registro local + BIP-39
- [ ] Chat E2E funcional
- [ ] Notificaciones sistema
- [ ] File system access

---

## Documentación y Operación

- [ ] `DEPLOYMENT_GUIDE.md` completo (deploy, rollback, monitoring)
- [ ] `BETA_TESTER_GUIDE.md` para testers
- [ ] `KNOWN_ISSUES.md` bugs conocidos + límites
- [ ] `CHANGELOG.md` v0.1.0-beta
- [ ] Script `beta_clients_ready.sh` funcional
- [ ] Healthcheck + métricas documentados

---

## Seguridad

- [ ] No claves privadas en logs
- [ ] TLS 1.3 en staging (termination en proxy)
- [ ] ADMIN_TOKEN rotado y seguro
- [ ] POSTGRES_PASSWORD seguro
- [ ] Rate limiting probado bajo carga
- [ ] Auditoría verifica sin PII
- [ ] WebAuthn configurado para admin (staging)

---

## Bugs Conocidos y Límites Beta

Ver `KNOWN_ISSUES.md`

---

## Firmas de Aprobación

| Rol | Nombre | Fecha | Firma |
|-----|--------|-------|-------|
| Tech Lead | | | |
| Security Review | | | |
| QA Lead | | | |
| Product Owner | | | |

---

## Próximos Pasos Post-Beta

1. Recopilar feedback testers (2 semanas)
2. Corregir bugs P1/P2
3. Hardening seguridad (auditoría externa)
4. Preparar v0.2.0 (E2E + WebSockets completos)
5. Documentar lecciones aprendidas