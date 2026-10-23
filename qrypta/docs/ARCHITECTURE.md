# Arquitectura y Políticas - Qrypta

## Visión General del Sistema

```
Cliente A                          Servidor de Enrutamiento                    Cliente B
├── Clave pública/privada Kyber    ├── No guarda contenido ni identidades      ├── Verifica firma con clave pública
├── Clave pública/privada Dilithium├── Enruta por ID de clave pública          ├── Recibe mensaje cifrado
├── Alias opcional firmado         └── Auditoría pública sin PII
└── Lista local de contactos
```

### Flujo de Mensajería
1. **Cliente A** firma mensaje con Dilithium
2. **Servidor** valida firma, enruta por `peer_id` (SHA3-256 de pubkey Dilithium)
3. **Cliente B** verifica firma y descifra con sesión Kyber/AES-256-GCM
4. **Auditoría** registra metadatos sin contenido ni PII

---

## Decisiones Técnicas (ADR)

| Área | Decisión | Justificación |
|------|----------|---------------|
| Servidor | Python 3.12 + FastAPI + Uvicorn | Async nativo, typing, ecosistema maduro |
| TUI Servidor | Textual (Python) | Terminal UI moderno, async, React-like |
| Dashboard Admin | React 18 + TypeScript + Vite + HTMX | Type safety, HMR, componentes reutilizables |
| Cliente Móvil | Flutter 3.x + Dart 3.x + Riverpod | Single codebase iOS/Android, performance |
| Cliente Web | React 18 + TypeScript + Vite + TanStack Query | Ecosistema web, SSR-ready, caching |
| Cliente Escritorio | Tauri v2 + Rust + React TS | Binarios nativos pequeños, seguridad |
| Criptografía PQC | liboqs (Kyber768, Dilithium3) | Estandarizado NIST, bindings multi-lenguaje |
| Cifrado Simétrico | AES-256-GCM | AEAD estándar, hardware-accelerated |
| KDF | Argon2id | Resistente a GPU/ASIC, memoria-dura |
| Recuperación | BIP-39 (24 palabras) | Estándar wallet, mnemotécnico humano |
| Peer ID | SHA3-256(pubkey_dilithium).hex() | Determinístico, colisión-resistente |

---

## Políticas de Seguridad

### Política de Gestión de Alias
- Alias opcionales firmados con Dilithium
- Múltiples alias permitidos por usuario
- Actualización y revocación por mensaje firmado
- No se vinculan a datos personales
- Verificación por contactos mediante firma

### Política de Auditoría Pública
- Código abierto del servidor
- Logs verificables sin contenido ni metadatos sensibles
- Auditorías externas periódicas
- Reportes de transparencia públicos
- Participación comunitaria en revisión

### Principios de Seguridad (Código)
- Nunca exponer claves privadas en logs
- Usar librerías de cifrado auditadas (liboqs, cryptography)
- Validar entradas de usuario siempre (Pydantic, Zod)
- TLS 1.3 obligatorio en todas las comunicaciones
- Certificate pinning en clientes móviles
- WebSocket WSS en web
- WebAuthn (FIDO2) obligatorio para admin
- Session timeout: 30 min admin
- Purga automática de datos usuario (configurable)

---

## Estructura del Monorepo

```
qrypta/
├── servidor/
│   ├── api/
│   │   ├── rutas.py
│   │   ├── websocket.py
│   │   ├── modelos.py
│   │   └── dashboard/
│   ├── auditoria/logger.py
│   ├── config/settings.py
│   ├── tui/configuracion.py
│   ├── dht/nodo.py
│   ├── push/notificaciones.py
│   ├── grupos/gestor.py
│   ├── tests/
│   ├── main.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── nucleo_crypto/
│   ├── crypto/
│   │   ├── keygen.py
│   │   ├── kem.py
│   │   ├── firma.py
│   │   ├── simetrico.py
│   │   └── sesion.py
│   ├── identidad/registro.py
│   ├── identidad/alias.py
│   ├── contactos/lista.py
│   ├── backup/exportar.py
│   ├── backup/importar.py
│   ├── recuperacion/mnemonic.py
│   ├── compartir/qr.py
│   ├── almacenamiento/local.py
│   ├── grupos/sala.py
│   ├── sync/sincronizacion.py
│   └── tests/
├── cliente_movil/
├── cliente_web/
├── cliente_escritorio/
├── docs/
│   ├── PLAN.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── BETA_READINESS_REPORT.md
│   └── archive/
└── .github/workflows/
```

---

## Roadmap por Fases (Resumen)

| Fase | Entregable Clave | Dependencia |
|------|------------------|-------------|
| 0 | Repo + CI base | — |
| 1 | Núcleo criptográfico (Kyber, Dilithium, AES, Argon2, BIP-39) | Bloquea todo lo criptográfico |
| 2 | Registro, identidad, alias, contactos, QR | Fase 1 |
| 3 | Backup cifrado export/import | Fase 1, 2 |
| 4 | Servidor REST base + Docker | Fase 1 |
| 5 | TUI configuración servidor | Fase 4 |
| 6 | Dashboard web admin | Fase 4 |
| 7 | Protocolo E2E completo (handshake, ratchet) | Fase 1, 2, 3 |
| 8 | WebSockets tiempo real | Fase 4, 7 |
| 9 | DHT descubrimiento pares | Fase 7, 8 |
| 10 | Push notifications (FCM/APNs) | Fase 8 |
| 11 | Grupos E2E + rotación clave | Fase 7, 8, 9 |
| 12 | Sync multi-dispositivo | Fase 3, 7, 8 |
| 13 | Clientes: Flutter, Web, Tauri | Fase 1-12 |
| 14 | CI/CD completo + semantic release + Docker publish | Fase 1-13 |

### Releases Sugeridas
- **0.1.0**: Servidor MVP (Fases 0, 1, 4, 5, 6)
- **0.2.0**: E2E + WebSockets (Fases 7, 8)
- **0.3.0**: DHT + Push + Grupos (Fases 9, 10, 11)
- **0.4.0**: Sync multi-dispositivo (Fase 12)
- **1.0.0**: Todos los clientes + CI/CD completo (Fases 13, 14)

---

## Criterios de Calidad
- Código modular y auditable
- Comentarios en español explicando lógica
- Funciones cortas (máx. 30 líneas)
- Pruebas unitarias para toda lógica crítica
- Sin claves privadas en logs
- Validación estricta de entrada
- Cumplimiento de `ESTYLEGUIDE.md`
- Coverage objetivo: 75%+ en clientes, 80%+ en núcleo/servidor