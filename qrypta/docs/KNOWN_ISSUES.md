# Bugs Conocidos y Límites Beta - Qrypta v0.1.0-beta

_Fecha: 2026-05-25_

---

## Bugs Conocidos (Prioridad P1/P2)

### P1 - Bloqueantes para Beta

| ID | Componente | Descripción | Workaround | Estado |
|----|------------|-------------|------------|--------|
| B-001 | nucleo_crypto | `oqs` no disponible en CI Ubuntu 24.04; tests PQC skipped | Tests core PASS; PQC validado localmente | Known |
| B-002 | cliente_movil | `flutter build ios` solo en macOS; no validado en CI | Build local macOS requerido | Known |
| B-003 | servidor | Rate limit usa memoria in-memory; no persistente multi-instancia | Single instance staging OK | Known |
| B-004 | DHT | Implementación local simplificada; no red Kademlia real | Funcional para LAN/staging | Known |

### P2 - Importantes

| ID | Componente | Descripción | Workaround | Estado |
|----|------------|-------------|------------|--------|
| B-005 | cliente_web | Service worker PWA básico; offline limited | Read-only cache | Known |
| B-006 | cliente_escritorio | Tauri updater no implementado | Manual reinstall | Known |
| B-007 | servidor | No métricas histográficas (solo instantáneas) | Prometheus + Grafana pending | Known |
| B-008 | push | FCM/APNs no configurado en staging; solo stub | Simulación local | Known |
| B-009 | backup | Backup grande (>10MB) puede timeout | Chunking pending | Known |

### P3 - Menores

| ID | Componente | Descripción | Workaround |
|----|------------|-------------|------------|
| B-010 | cliente_web | Emoji picker no cierra al click fuera | Click fuera manual |
| B-011 | cliente_movil | Landscape layout chat mejorable | Portrait recomendado |
| B-012 | TUI admin | SQL browser solo SELECT | Por diseño (seguridad) |

---

## Límites de la Beta

### Alcance Funcional
| Función | Estado Beta | Notas |
|---------|-------------|-------|
| Registro local + identidad | ✅ Completo | BIP-39, alias, QR |
| Chat 1:1 E2E | ✅ Completo | Kyber + Dilithium + ratchet |
| Grupos E2E | ✅ Completo | Rotación clave al expulsar |
| Sync multi-dispositivo | ✅ Completo | Vincular, transferir, revocar |
| Push notifications | ⚠️ Parcial | Stub local; FCM/APNs no configurado |
| DHT descubrimiento | ⚠️ Parcial | Local map; no red P2P real |
| Backup/restore | ✅ Completo | AES-256-GCM + Argon2id |
| Auditoría servidor | ✅ Completo | Sin PII, logs verificables |
| Dashboard admin | ✅ MVP | Métricas, usuarios, auditoría |
| TUI admin | ✅ MVP | Logs, users, rate limit, SQL |

### Límites Técnicos
| Límite | Valor | Justificación |
|--------|-------|---------------|
| Mensajes por peer (cola) | 500 | Memoria servidor |
| TTL mensajes pendientes | 24h | Configurable |
| Tamaño archivo adjunto | 10MB | Memoria + red |
| Miembros por grupo | 50 | Rotación clave O(n) |
| Dispositivos vinculados | 5 | UX + seguridad |
| Rate limit API | 30/min | Anti-abuso básico |

### Límites de Entorno
- **Staging**: Single instance, HTTP (TLS en proxy), BD local
- **CI**: Ubuntu 24.04 runners, `oqs` skipped, no iOS build
- **Clientes**: Web PWA, Android APK, Linux/Windows Tauri (no iOS, no macOS)

---

## Deuda Técnica Post-Beta

1. **oqs en CI**: Compilar liboqs desde fuente en workflow
2. **DHT real**: Kademlia sobre libp2p o implementación propia
3. **Push real**: FCM/APNs configurado + tokens persistentes
4. **Multi-instancia servidor**: Redis para rate limit + cola distribuida
5. **Tauri updater**: Firma + auto-update
6. **iOS build**: macOS runner en CI + certificates
7. **Métricas históricas**: Prometheus + Grafana stack
8. **Load testing**: k6 scripts + CI gate

---

## Reporte de Issues

Para reportar bugs durante beta:
1. Ejecutar `scripts/beta_clients_ready.sh` y adjuntar output
2. Capturar logs: `docker-compose logs servidor` + cliente console
3. Crear issue en GitHub con:
   - Template: `Bug Report`
   - Labels: `beta`, `p1|p2|p3`, componente
   - Pasos reproducción
   - Output esperado vs actual
   - Entorno (OS, cliente, versión)