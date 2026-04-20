# Plan Detallado: Fase 13 + Administración
## Cliente Múltiple + Paneles de Control
**Versión 3.0** | Generado: 19 de abril de 2026

### Estado de Ejecución (actualizado: 20 de abril de 2026)
- Cliente Web: UI MVP avanzada + realtime base + PWA base + tests Vitest/RTL en verde.
- Dashboard Admin Web: páginas core + métricas realtime/alertas + seguridad base + tests en verde.
- Consola Admin (TUI): mejoras iniciales aplicadas (comandos y métricas básicas).
- Cliente Escritorio (Tauri): UI MVP avanzada + tests React en verde + build en verde.
- Cliente Móvil (Flutter): estructura base + identidad/E2E con PQC base y ratchet + tests/analyze en verde.
**Actualizado: 20 de abril de 2026 (sesión 2)**
- Cliente Web: cobertura 78.76% stmts / 81.13% lines / 75% funcs — 51 tests (vitest + playwright). ✅
- Dashboard Admin Web: audit trail + JWT/WebAuthn + Playwright E2E. ✅
- AdminTUI: Textual 6.1.0 + usuarios ban/unban + rate limit + SQL browser + 16 tests. ✅
- Bloqueantes activos: cargo (Tauri 13c), Android SDK (Flutter 13a.8). Ver GUIA_DESBLOQUEO_ENTORNO.md.

---

## 📋 VISIÓN GENERAL

Completar la Fase 13 (clientes multiplataforma) e implementar paneles de administración modernos para gestión centralizada del servidor, usuarios, auditoría y métricas.

### Objetivos Clave
1. **Clientes producción-ready**: Flutter (móvil), React (web), Tauri (escritorio)
2. **Administración escalable**: Dashboard web moderno + consola TUI mejorada
3. **Experiencia usuario unificada**: UI/UX consistente, accesible, responsiva
4. **Seguridad y auditoría**: Trazabilidad completa de operaciones admin

---

## 🛠️ STACK TECNOLÓGICO RECOMENDADO

### **Cliente Flutter (Android/iOS)**
- **Framework**: Flutter 3.x + Dart 3.x
- **State Management**: Riverpod 2.x (reactivo, modular)
- **Local Storage**: Hive + SQLite (isar para queries complejas)
- **Criptografía**: liboqs-dart (Kyber, Dilithium), pointycastle (AES-GCM)
- **UI Components**: Material 3 + flutter_staggered_grid_view
- **Redes**: Dio + WebSocket (connection_pool)
- **Testing**: Flutter test + mocktail

### **Cliente Web (React/TypeScript)**
- **Framework**: React 18.x + TypeScript 5.x
- **Build Tool**: Vite 5.x (SSR-ready)
- **State Management**: TanStack Query (data sync) + Zustand (UI state)
- **UI Library**: shadcn/ui + Tailwind CSS 3.x
- **Criptografía**: liboqs-wasm (compilado a WebAssembly) o crypto-js
- **Redes**: TanStack Query + socket.io-client
- **Testing**: Vitest + React Testing Library
- **PWA Support**: workbox para offline

### **Cliente Escritorio (Tauri v2)**
- **Framework**: Tauri 2.x + React 18.x + TypeScript
- **Backend Rust**: Tauri core + tokio async
- **Criptografía**: liboqs-rust (FFI bindings)
- **UI**: Misma que web (React + Tailwind)
- **Desktop Features**: File system, clipboard, system notifications
- **Updater**: Tauri built-in (signature-based)
- **Testing**: vitest + @testing-library/react

### **Dashboard Admin Web**
- **Framework**: React 18.x + TypeScript
- **Build**: Vite 5.x + Turborepo (monorepo)
- **Charts/Stats**: Recharts + lucide-react (icons)
- **UI**: shadcn/ui + Tailwind + Framer Motion (animations)
- **Auth**: JWT + WebAuthn (FIDO2)
- **Real-time**: WebSocket + SockJS fallback
- **Monitoring**: Grafana integration (metrics export)
- **Testing**: Vitest + Playwright (E2E)

### **Consola Admin (TUI)**
- **Framework**: Textual 0.40.x (Python, Terminal UI)
- **Async**: Anyio + asyncio
- **Logging**: Python logging + structlog (JSON)
- **DB Access**: SQLAlchemy + psycopg2
- **Notifications**: Rich + click (CLI enhancements)
- **Real-time**: WebSocket + async generators

---

## 📁 ESTRUCTURA DE CARPETAS

```
qrypta/
├── servidor/
│   ├── api/
│   ├── auditoria/
│   ├── admin_consola/           [NEW] Consola TUI mejorada
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── components/
│   │   ├── models/
│   │   └── utils/
│   ├── dashboard_admin_web/     [NEW] React dashboard
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   └── store/
│   │   ├── vite.config.ts
│   │   └── package.json
│   └── ...
├── nucleo_crypto/
├── cliente_movil/
│   ├── lib/
│   │   ├── main.dart
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── chat/
│   │   │   ├── contacts/
│   │   │   └── settings/
│   │   ├── shared/
│   │   └── config/
│   └── pubspec.yaml
├── cliente_web/                 [NEW] React web app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── services/
│   ├── vite.config.ts
│   └── package.json
├── cliente_escritorio/          [NEW] Tauri desktop
│   ├── src-tauri/
│   │   ├── src/
│   │   ├── tauri.conf.json
│   │   └── Cargo.toml
│   ├── src/
│   │   ├── components/
│   │   └── main.tsx
│   └── package.json
└── docs/
    ├── PLAN.md (maestro)
    ├── API_SPEC.md
    ├── ADMIN_GUIDE.md
    └── DATABASE_SCHEMA.md
```

---

## 🎯 FASES DETALLADAS

### **FASE 13a: Cliente Flutter**

#### 13a.1 - Setup y Configuración
- [x] Configurar pubspec.yaml completo (MVP)
  - Dependencias core: riverpod, hive, dio, sqflite
  - Dependencias PQC: pendiente liboqs (bindings Dart)
  - Testing: flutter_test, mocktail
- [x] Configurar CI/CD (GitHub Actions checks + build Android/iOS)
- [x] Setup Firebase FCM para push notifications (base)
- [x] Crear estructura base de carpetas (features, shared, config)

**Tiempo estimado**: 2-3 días | **Branch**: feature/cliente-flutter

#### 13a.2 - Capa de Data
- [x] Implementar HiveAdapter para modelos locales
- [x] Crear LocalStorage service (key-value)
- [x] Implementar SQLite para caché de mensajes
- [x] Crear DI (dependency injection) container

**Tiempo estimado**: 2-3 días

#### 13a.3 - Criptografía e Identidad
- [x] Integrar liboqs-dart para Kyber + Dilithium
- [x] Implementar KeyStore local (Secure Storage)
- [x] Crear módulo de registro BIP-39 (24 palabras)
- [x] Implementar ExportPrivateKey (PKCS#8 encriptado) [MVP]

**Tiempo estimado**: 3-4 días

#### 13a.4 - Protocolo E2E
- [x] Handshake de firma (Ed25519 + Dilithium ML-DSA)
- [x] Encapsulación de sesión (Kyber/ML-KEM + fallback placeholder)
- [x] Cifrado/Descifrado por mensaje (AES-256-GCM)
- [x] Forward secrecy (ratchet de claves)

**Tiempo estimado**: 3-4 días

#### 13a.5 - Networking y Sincronización
- [x] REST client (Dio con interceptors) [MVP]
- [x] WebSocket cliente [MVP]
- [x] Estado de conexión (online/offline) [MVP presencia]
- [x] Sync automático de mensajes y contactos [MVP]

**Tiempo estimado**: 2-3 días

#### 13a.6 - UI/UX (Cliente Flutter)
- [x] Screens: Login, RecuperarBackup, ContactosList, ChatScreen, Ajustes
- [x] Material 3 design system + theming
- [x] Adaptive layouts (phone, tablet)
- [x] Dark mode support
- [x] Formularios validados (flutter_form_builder)

**Tiempo estimado**: 4-5 días

#### 13a.7 - Testing
- [x] Unit tests (crypto, storage, models) - base implementada
- [x] Widget tests (UI components)
- [x] Integration tests (full user flow) [base implementada; ejecución requiere dispositivo/emulador]
- [x] Setup SonarQube para análisis (config base)

**Tiempo estimado**: 2-3 días

#### 13a.8 - Release Flutter
- [ ] Build APK/AAB (Android)
- [ ] Build IPA (iOS)
- [ ] Merge a develop
- [ ] Tag v0.5.0-flutter-rc1

**Tiempo estimado**: 1-2 días

---

### **FASE 13b: Cliente Web**

#### 13b.1 - Scaffolding Vite + React + TypeScript
- [x] Crear proyecto Vite con template React + TS
- [x] Configurar Tailwind + shadcn/ui (base utilidades/componentes)
- [x] Linter (ESLint) + Prettier
- [x] Husky + lint-staged para pre-commit hooks

**Tiempo estimado**: 1-2 días | **Branch**: feature/cliente-web

#### 13b.2 - Criptografía en Navegador
- [ ] Compilar liboqs a WebAssembly (WASM)
- [x] Crear crypto service en TypeScript
- [x] IndexedDB para persistencia local
- [x] Session storage para keys en memoria (temporal)

**Tiempo estimado**: 3-4 días

#### 13b.3 - State Management
- [x] TanStack Query para server state
- [x] Zustand para UI state
- [x] Devtools + Redux DevTools extension (zustand middleware)
- [x] Custom hooks (useAuth, useChat, useContacts)

**Tiempo estimado**: 2-3 días

#### 13b.4 - Autenticación y Registro
- [x] Login con BIP-39 recovery
- [x] Registro local (generar keys)
- [x] Password manager integration (WebAuthn) [base]
- [x] JWT token management + refresh

**Tiempo estimado**: 2-3 días

#### 13b.5 - Interfaz Principal
- [x] Sidebar de contactos
- [x] Chat window con threading
- [x] Rich text editor con emoji picker
- [x] File upload/download
- [x] Config panel (profile, privacy, notifications)

**Tiempo estimado**: 4-5 días

#### 13b.6 - Real-time
- [x] WebSocket integración (MVP con WebSocket nativo)
- [x] Typing indicators
- [x] Online/offline status
- [x] Message delivery notifications

**Tiempo estimado**: 2-3 días

#### 13b.7 - PWA Features
- [x] Service worker (implementación base manual)
- [x] Offline mode (read cache)
- [x] Install prompt
- [x] Push notifications (base)

**Tiempo estimado**: 2-3 días

#### 13b.8 - Testing
- [x] Vitest para unit tests
- [x] React Testing Library para components
- [x] Playwright para E2E
- [x] Coverage target: 75%+ (78.76% stmts, 81.13% lines, 75% funcs — 51 tests)

**Tiempo estimado**: 2-3 días

#### 13b.9 - Deployment
- [x] Build optimization (tree-shaking, code splitting)
- [ ] Deploy a staging (Netlify/Vercel)
- [ ] Merge a develop

**Tiempo estimado**: 1-2 días

---

### **FASE 13c: Cliente Tauri**

#### 13c.1 - Scaffolding Tauri v2
- [x] Crear proyecto Tauri
- [x] Reutilizar código React anterior (MVP visual)
- [x] Configurar Cargo.toml y tauri.conf.json
- [x] Setup dev environment

**Tiempo estimado**: 1-2 días | **Branch**: feature/cliente-escritorio

#### 13c.2 - Backend Rust + FFI
- [ ] Crear módulos Rust para Tauri
- [ ] FFI bindings con liboqs-rust
- [ ] File system operations (encriptadas)
- [ ] System tray integration

**Tiempo estimado**: 3-4 días

#### 13c.3 - Desktop Features
- [x] File drag-and-drop
- [x] Clipboard manager
- [x] System notifications
- [ ] OS native dialogs

**Tiempo estimado**: 2-3 días

#### 13c.4 - UI/UX (Tauri)
- [x] Adaptar React components para desktop
- [x] Window controls (min/max/close custom)
- [x] Menu bar + context menus
- [x] Keyboard shortcuts

**Tiempo estimado**: 2-3 días

#### 13c.5 - Updater
- [ ] Tauri built-in updater
- [ ] Signature validation
- [ ] Background update check
- [ ] User notifications

**Tiempo estimado**: 1-2 días

#### 13c.6 - Testing
- [ ] Cargo test para Rust
- [x] Vitest para React parts
- [ ] Tauri-specific tests

**Tiempo estimado**: 1-2 días

#### 13c.7 - Build y Release
- [ ] Build para Windows (.msi)
- [ ] Build para Linux (.deb, .appimage)
- [ ] Code signing (optional)
- [ ] Merge a develop

**Tiempo estimado**: 1-2 días

---

### **FASE Admin-Web: Dashboard de Administración**

#### Admin.1 - Scaffolding y Setup
- [x] Proyecto React + TypeScript + Vite
- [x] Tailwind + shadcn/ui (base)
- [x] Autenticación con JWT + WebAuthn (base)
- [x] Estructura base (pages, hooks, store)

**Tiempo estimado**: 2-3 días | **Branch**: feature/admin-dashboard-web

#### Admin.2 - Páginas Core
- [x] Dashboard (overview, metrics, alerts)
- [x] Usuarios (MVP: listado + cambio de estado)
- [x] Servidores (MVP: status + reinicio base)
- [x] Auditoría (MVP: eventos + filtros + export)
- [x] Configuración (MVP: rate limiting, sesiones, retención)

**Tiempo estimado**: 4-5 días

#### Admin.3 - Real-time y Métricas
- [x] WebSocket para stats en vivo (MVP + fallback)
- [ ] Grafana/Prometheus integration
- [x] Charts con Recharts
- [x] Alert system

**Tiempo estimado**: 3-4 días

#### Admin.4 - Seguridad
- [x] RBAC (Role-Based Access Control) [MVP]
- [x] 2FA (TOTP) [MVP demo]
- [x] Session management [MVP]
- [x] Audit trail de cambios

**Tiempo estimado**: 2-3 días

#### Admin.5 - Testing y Deploy
- [x] E2E con Playwright
- [ ] Performance testing
- [ ] Deploy a staging

**Tiempo estimado**: 2-3 días

---

### **FASE Admin-Consola: TUI Mejorada**

#### AdminTUI.1 - Refactor Textual
- [x] Upgrade a Textual 0.40.x (ya en 6.1.0)
- [x] Mejorar layout (salida con colores, tablas)
- [x] Widgets modernos (Header, Footer, Static, Input con bindings)
- [x] Async/await para operaciones no-bloqueantes

**Tiempo estimado**: 2-3 días | **Branch**: feature/admin-consola

#### AdminTUI.2 - Funcionales
- [x] Ver estado servidor real-time
- [x] Gestión de usuarios (ban/unban)
- [x] View logs con filtros (básico: comando `tail N`)
- [x] Estadísticas de tráfico
- [x] Control de rate limits (rate show / rate set)

**Tiempo estimado**: 3-4 días

#### AdminTUI.3 - Raw SQL / Database browser
- [x] Ejecutar queries directas (solo SELECT, seguro)
- [x] Browse tables interactivamente (sql tables / sql select)
- [x] Export data (CSV, JSON) (export csv / export json)

**Tiempo estimado**: 2-3 días

#### AdminTUI.4 - Testing y Release
- [x] Testing TUI components (16 tests en test_tui_configuracion.py)
- [ ] Merge a develop

**Tiempo estimado**: 1-2 días

---

## 📊 CRONOGRAMA

| Fase | Componente | Duración | Fecha Inicio | Fecha Fin |
|------|-----------|----------|-------------|-----------|
| 13a | Flutter MVP | 5-6 semanas | Apr 21 | Jun 2 |
| 13b | Web MVP | 4-5 semanas | Jun 3 | Jul 7 |
| 13c | Tauri MVP | 3-4 semanas | Jul 8 | Aug 5 |
| Admin-Web | Dashboard | 2-3 semanas | Aug 6 | Aug 27 |
| Admin-TUI | Consola | 1-2 semanas | Aug 28 | Sep 10 |
| **Total** | **Fase 13 + Admin** | **~16-20 semanas** | **Apr 21** | **Sep 10** |

---

## 🔒 CONSIDERACIONES DE SEGURIDAD

1. **Keys Management**
   - Nunca exponer privadas en logs
   - Secure Storage (Android Keystore, iOS Keychain, libsecret Linux)
   - Encrypted at rest (AES-256-GCM)

2. **Comunicación**
   - TLS 1.3 (enforce)
   - Certificate pinning (móvil)
   - WebSocket WSS (web)

3. **Admin Access**
   - WebAuthn (FIDO2) obligatorio
   - IP whitelist (configurables)
   - Session timeout: 30 min
   - Audit log de todo

4. **User Data**
   - End-to-end encrypted
   - No metadata en servidor
   - Purga automática (configurable)

---

## 📈 MÉTRICAS DE ÉXITO

- ✅ Todos los clientes con 75%+ test coverage
- ✅ Latencia E2E < 100ms
- ✅ Load test: 1000 concurrent users
- ✅ Uptime: 99.5%+
- ✅ Security audit: 0 critical issues
- ✅ User experience: Mobile 90+/100 (Lighthouse)

---

## 🚀 NEXT STEPS

1. **Semana 1 (Abr 21-27)**: Flutter setup + criptografía
2. **Semana 2-3**: Flutter E2E + UI
3. **Semana 4-5**: Flutter testing + release
4. *[Paralelo]* **Semana 3-7**: Web scaffolding → testing
5. *[Paralelo]* **Semana 8-11**: Tauri scaffolding → release
6. *[Paralelo]* **Semana 12-14**: Admin Dashboard
7. *[Paralelo]* **Semana 15-16**: Admin Consola

---

## ⛔ BLOQUEANTES DE ENTORNO ACTUALES

- Android SDK no disponible en entorno actual (impide `flutter build apk`).
- `cargo` (toolchain Rust) no disponible en entorno actual (impide `cargo test` y build nativo Tauri completo).
- Build iOS (`flutter build ipa`) no es ejecutable en Linux (requiere macOS + Xcode).
- Ejecución de `integration_test` Flutter requiere dispositivo/emulador compatible conectado.
- Descarga automática de toolchains externas bloqueada en este entorno por política de ejecución (subcomandos `curl`/`wget`) y ausencia de privilegios sudo en sesión actual.
- Deploy a staging (Netlify/Vercel/Azure) pendiente de credenciales/entorno objetivo.
- Integración FCM y WebAuthn productiva requiere configuración de servicios externos y secretos.

---

**¿Apruebas este plan detallado? ¿Deseas ajustes en tecnologías, cronograma o prioridades?**
