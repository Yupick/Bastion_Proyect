# Guía de Tester Beta - Qrypta v0.1.0-beta

_Fecha: 2026-05-25_

---

## Bienvenida

¡Gracias por participar en el beta test de Qrypta! Tu feedback es crucial para pulir el sistema antes del lanzamiento público.

### Qué es Qrypta
Sistema de mensajería híbrido post-cuántico con:
- **Privacidad radical**: E2E real, servidor no ve contenido ni identidades
- **Criptografía PQC**: Kyber768 (KEM) + Dilithium3 (firmas) resistente a cuánticos
- **Multi-dispositivo**: Sync seguro entre móvil, web y escritorio
- **Auditoría verificable**: Código abierto, logs sin PII

---

## Acceso a Staging

### URLs
| Componente | URL |
|------------|-----|
| Servidor API | `https://staging.qrypta.app` |
| Dashboard Admin | `https://staging.qrypta.app/admin` (requiere token) |
| Métricas | `https://staging.qrypta.app/metrics` |

### Credenciales
- **Admin Token**: Se proporcionará por canal seguro (no commitear)
- **Registro**: Auto-registro local en cada cliente (BIP-39 24 palabras)

---

## Instalación Clientes

### Cliente Web (PWA)
1. Abrir `https://staging.qrypta.app` en Chrome/Edge/Firefox
2. Click "Instalar" en barra direcciones → "Instalar Qrypta"
3. Funciona offline (solo lectura cache)

### Cliente Android
```bash
# Opción A: Descargar APK desde GitHub Releases
# Opción B: Build local
cd qrypta/cliente_movil
flutter build apk --release
# Instalar build/app/outputs/flutter-apk/app-release.apk
```

### Cliente Escritorio (Windows/Linux)
```bash
# Descargar desde GitHub Releases (MSI / AppImage / DEB)
# O build local:
cd qrypta/cliente_escritorio
npm run build
cargo tauri build
```

---

## Primeros Pasos (Onboarding)

### 1. Crear Identidad
1. Abrir cliente → "Crear nueva identidad"
2. **GUARDAR LAS 24 PALABRAS** (BIP-39 mnemonic)
   - ⚠️ **CRÍTICO**: Sin ellas NO hay recuperación
   - Escríbelas en papel, guárdalas seguro
3. Confirmar palabras en orden
4. Establecer alias opcional (firmado con Dilithium)

### 2. Agregar Contacto
1. "Agregar contacto" → Escanear QR o pegar código
2. Verificar fingerprint (primeros 8 chars peer_id)
3. Contacto aparece en lista

### 3. Enviar Primer Mensaje
1. Click contacto → Nueva conversación
2. Escribir mensaje → Enviar
3. Verificar: ✅ Entregado, 🔒 Cifrado E2E

---

## Casos de Prueba Prioritarios

### P0 - Críticos (Deben funcionar)
| Test | Pasos | Resultado Esperado |
|------|-------|-------------------|
| T-001 | Registro + backup + restore | Restore recupera identidad exacta |
| T-002 | Chat 1:1 E2E | Mensaje cifrado, solo destinatario lee |
| T-003 | Sync 2 dispositivos | 2do dispositivo ve historial completo |
| T-004 | Grupo crear + miembro | Mensajes grupo cifrados, rotación al expulsar |
| T-005 | Push offline | Dispositivo offline recibe aviso |

### P1 - Importantes
| Test | Pasos | Resultado Esperado |
|------|-------|-------------------|
| T-010 | Alias actualizar/revocar | Contactos ven cambio firmado |
| T-011 | Revocar dispositivo | Dispositivo revocado no sync |
| T-012 | DHT publicar/buscar | Peer visible y expira TTL |
| T-013 | Rate limit | 31 req/min → 429 |
| T-014 | Auditoría | Logs sin contenido ni PII |

### P2 - Deseables
| Test | Pasos | Resultado Esperado |
|------|-------|-------------------|
| T-020 | PWA offline | Leer mensajes cache sin red |
| T-021 | Tauri notificaciones | Notificación sistema al recibir |
| T-022 | Backup grande | >10MB export/import OK |
| T-023 | Múltiples grupos | 5+ grupos simultáneos |

---

## Cómo Reportar Bugs

### Canal: GitHub Issues
1. Ir a: https://github.com/Yupick/Bastion_Proyect/issues/new
2. Seleccionar template: **"Beta Bug Report"**
3. Completar:

```markdown
## Entorno
- Cliente: [Web / Android / Windows / Linux]
- Versión: [ej. v0.1.0-beta.1]
- OS: [ej. Android 14, Windows 11, Ubuntu 24.04]

## Pasos para Reproducir
1. 
2. 
3. 

## Resultado Esperado


## Resultado Actual


## Logs / Capturas
- Adjuntar: `scripts/beta_clients_ready.sh` output
- Logs cliente (consola DevTools / logcat / journalctl)
- Logs servidor (si relevante): `docker-compose logs servidor`

## Severidad
- [ ] P1 - Bloqueante (no puedo usar feature core)
- [ ] P2 - Importante (workaround existe)
- [ ] P3 - Menor (cosmético/mejora)
```

### Logs Útiles

**Cliente Web**: F12 → Console → Filtrar `[Qrypta]`
**Android**: `adb logcat | grep -i qrypta`
**Escritorio**: `journalctl -u qrypta` o consola DevTools
**Servidor**: `docker-compose logs -f servidor`

---

## Checklist de Sesión de Prueba

Marca al completar:

- [ ] Identidad creada + 24 palabras guardadas
- [ ] Backup exportado + importado en 2do dispositivo
- [ ] Contacto agregado + chat 1:1
- [ ] Mensaje enviado + recibido + verificado E2E
- [ ] Grupo creado + miembro agregado + mensaje grupo
- [ ] Miembro expulsado → no lee nuevos
- [ ] Dispositivo revocado → no sync
- [ ] Push: mensaje offline → aviso recibido
- [ ] DHT: peer publicado → buscable → expira
- [ ] Rate limit probado
- [ ] Dashboard admin: métricas + auditoría visibles

---

## Feedback Cualitativo

Además de bugs, queremos tu opinión:

| Aspecto | 1-5 | Comentarios |
|---------|-----|-------------|
| Facilidad onboarding | | |
| UX chat | | |
| Velocidad sync | | |
| Claridad backup/restore | | |
| Confianza seguridad | | |
| Estabilidad general | | |

**¿Qué faltaría para usar Qrypta diario?**

**¿Qué rompería tu confianza en el sistema?**

---

## Contacto Soporte Beta

| Canal | Uso |
|-------|-----|
| GitHub Issues | Bugs + feature requests |
| Discord #qrypta-beta | Chat tiempo real (invite privado) |
| Email | security@qrypta.app (solo seguridad) |

---

## Agradecimientos

Tu participación hace Qrypta más seguro. Al final del beta, recibirás:
- Acceso anticipado v1.0
- Créditos en CONTRIBUTORS.md
- Swag Qrypta (stickers, etc.)

¡Gracias! 🔐