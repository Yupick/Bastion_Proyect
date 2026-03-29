# Plan Maestro: Sistema de Mensajeria Hibrido PQC - Qrypta

_Generado: 29 de marzo de 2026 - Version 2.0_

## TL;DR
Qrypta se implementa como monorepo con GitFlow, servidor Python/FastAPI en contenedor Docker (y ejecucion local para desarrollo), TUI de configuracion (Textual), dashboard web (HTMX), y clientes para Android+iOS, Web, Windows y Linux.

Incluye, dentro de la hoja de ruta:
- Protocolo E2E completo con sesiones (Kyber + Dilithium)
- Sincronizacion multi-dispositivo en tiempo real
- Notificaciones push y WebSockets
- Descubrimiento de pares por DHT
- Mensajes de grupo con control criptografico de membresia

## Decisiones tecnicas
- Servidor: Python 3.12 + FastAPI + Uvicorn
- TUI servidor: Textual
- Dashboard: HTML + HTMX + CSS
- Android+iOS: Flutter (Dart)
- Web: TypeScript + React (Vite)
- Desktop Windows+Linux: Tauri v2 (Rust + React TS)
- Criptografia PQC: liboqs (Kyber768, Dilithium3)
- Cifrado simetrico: AES-256-GCM
- KDF: Argon2id
- Recuperacion: BIP-39 (24 palabras)
- peer_id: SHA3-256(pubkey_dilithium).hex()

## Estructura objetivo del monorepo

```text
qrypta/
|- servidor/
|  |- api/
|  |  |- rutas.py
|  |  |- websocket.py
|  |  |- modelos.py
|  |  `- dashboard/
|  |- auditoria/logger.py
|  |- config/settings.py
|  |- tui/configuracion.py
|  |- dht/nodo.py
|  |- push/notificaciones.py
|  |- grupos/gestor.py
|  |- tests/
|  |- main.py
|  |- Dockerfile
|  |- docker-compose.yml
|  `- requirements.txt
|- nucleo_crypto/
|  |- crypto/
|  |  |- keygen.py
|  |  |- kem.py
|  |  |- firma.py
|  |  |- simetrico.py
|  |  `- sesion.py
|  |- identidad/registro.py
|  |- identidad/alias.py
|  |- contactos/lista.py
|  |- backup/exportar.py
|  |- backup/importar.py
|  |- recuperacion/mnemonic.py
|  |- compartir/qr.py
|  |- almacenamiento/local.py
|  |- grupos/sala.py
|  |- sync/sincronizacion.py
|  `- tests/
|- cliente_movil/
|- cliente_web/
|- cliente_escritorio/
|- docs/
|  |- PLAN.md
|  |- ADR/
|  `- api/
`- .github/workflows/
```

## GitFlow
- main: versiones estables
- develop: integracion continua
- feature/*: nuevas funcionalidades
- release/x.y.z: preparacion de version
- hotfix/*: correcciones criticas

## Roadmap por fases

### Fase 0 - Setup del repositorio
1. Inicializar repo con ramas main y develop
2. Crear estructura de carpetas y placeholders
3. Configurar .gitignore (Python, Flutter, Node, Rust, .env)
4. Definir CI inicial para servidor

### Fase 1 - Nucleo criptografico base
1. Generacion de claves Kyber y Dilithium
2. KEM (encapsular/desencapsular)
3. Firma digital (firmar/verificar)
4. Cifrado simetrico AES-256-GCM
5. Recuperacion BIP-39 (24 palabras)
6. Almacenamiento local cifrado con Argon2id

### Fase 2 - Registro, identidad y alias
1. Registro local sin contacto con servidor
2. peer_id derivado de clave publica Dilithium
3. Alias opcionales firmados
4. Actualizacion/revocacion de alias por firma
5. Contactos locales sin base central
6. Compartir claves por QR/codigo/enlace

### Fase 3 - Backup cifrado
1. Exportar .pqcbackup con AES-256-GCM y Argon2id
2. Incluir checksum y firma del backup
3. Importar validando magic/version/checksum/firma
4. Manejo de errores tipados (password invalida, firma invalida, backup corrupto)

### Fase 4 - Servidor base REST
1. Endpoints de mensajeria minima
2. Cola en memoria con TTL
3. Rate limiting
4. Auditoria publica sin PII
5. Configuracion por .env
6. Dockerfile y docker-compose

### Fase 5 - TUI de configuracion del servidor
1. Ver estado
2. Editar configuracion
3. Consultar logs
4. Limpiar cola de mensajes

### Fase 6 - Dashboard web
1. Estado operativo
2. Metricas agregadas
3. Ultimos eventos auditables
4. Vista publica + administracion con token

### Fase 7 - Protocolo E2E completo
1. Handshake firmado con Dilithium
2. Sesion inicial con Kyber
3. Ratchet de claves para forward secrecy
4. Cifrado por mensaje y soporte out-of-order

### Fase 8 - WebSockets y tiempo real
1. Canal WS autenticado por firma
2. Entrega directa si peer conectado
3. Fallback a cola REST si peer desconectado
4. Heartbeat y reconexion

### Fase 9 - Descubrimiento de pares con DHT
1. Nodo Kademlia adaptado
2. Publicacion de endpoint firmada
3. Busqueda de peer por peer_id
4. TTL y renovacion de registros

### Fase 10 - Notificaciones push
1. Registro de token por dispositivo
2. Envio de aviso "mensaje pendiente" sin contenido sensible
3. Integracion FCM/APNs
4. Baja de token y controles de privacidad

### Fase 11 - Mensajes de grupo
1. Creacion de sala
2. Alta/baja de miembros con firma del admin
3. Clave de grupo y rotacion al expulsar miembros
4. Enrutamiento de mensajes de grupo sin acceso a contenido por servidor

### Fase 12 - Sincronizacion multi-dispositivo
1. Vinculacion de nuevo dispositivo por firma del maestro
2. Transferencia cifrada de estado inicial
3. Sincronizacion de mensajes y estados de lectura
4. Revocacion de dispositivo comprometido

### Fase 13 - Clientes
- 13a: Flutter (Android+iOS)
- 13b: React/TS (Web)
- 13c: Tauri (Windows+Linux)

Incluye en todos:
1. Registro local
2. E2E
3. Grupos
4. Sync
5. Backup/restore

### Fase 14 - CI/CD completo
1. Pipelines para servidor y nucleo
2. Pipelines para web y movil
3. Build y versionado semantico
4. Publicacion de imagen Docker del servidor

## Dependencias de alto nivel
- Fase 1 bloquea lo criptografico de todo el sistema
- Fase 4 habilita integracion temprana de clientes
- Fase 7 es prerequisito de grupos E2E
- Fase 8 habilita tiempo real y base para sync
- Fase 11 depende de Fases 7, 8 y 9
- Fase 12 depende de backup + sesiones + tiempo real

## Releases sugeridas
- 0.1.0: Servidor MVP (Fases 0, 1, 4, 5, 6)
- 0.2.0: E2E + WebSockets (agrega Fases 7 y 8)
- 0.3.0: DHT + Push + Grupos (agrega Fases 9, 10, 11)
- 0.4.0: Sync multi-dispositivo (agrega Fase 12)
- 1.0.0: Todos los clientes productivos + CI/CD completo (Fases 13 y 14)

## Criterios de calidad
- Codigo modular y auditable
- Comentarios en espanol
- Funciones cortas (ideal <= 30 lineas)
- Pruebas unitarias para toda logica critica
- Sin claves privadas en logs
- Validacion estricta de entrada
- Cumplimiento de ESTYLEGUIDE.md
