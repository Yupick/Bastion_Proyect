# Guía de Desarrollo - Qrypta

## Setup de Entorno (Onboarding)

### Requisitos Base
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y \
  python3.12 python3.12-venv python3-pip \
  nodejs npm \
  docker.io docker-compose \
  git curl wget

# Rust (para Tauri)
curl https://sh.rustup.rs -sSf | sh -s -- -y
source "$HOME/.cargo/env"
rustup target add x86_64-unknown-linux-gnu

# Flutter (para móvil)
# Ver opción CLI abajo o instalar Android Studio
```

### Dependencias Nativas Críticas

#### 1) liboqs / Python binding `oqs` (PQC)
```bash
# Opción A: pip (requiere liboqs en sistema)
pip install oqs

# Opción B: Compilar desde fuente (si pip falla)
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs && mkdir build && cd build
cmake -DOQS_BUILD_ONLY_LIB=OFF -DCMAKE_INSTALL_PREFIX=/usr/local ..
make -j$(nproc) && sudo make install
pip install oqs
```

#### 2) Rust/Cargo para Tauri (Cliente Escritorio)
```bash
# Ya instalado via rustup arriba
cargo --version  # verificar
```

#### 3) Android SDK para Flutter Release
```bash
# Opción CLI (headless)
mkdir -p "$HOME/Android/Sdk/cmdline-tools"
# Descargar commandline-tools de developer.android.com
# Descomprimir en: $HOME/Android/Sdk/cmdline-tools/latest

export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
flutter config --android-sdk "$ANDROID_HOME"
flutter doctor -v
```

#### 4) iOS Build
Solo posible en macOS con Xcode. En Linux/CI: usar GitHub Actions macOS runners.

---

## Estructura de Proyectos por Componente

### Servidor (`qrypta/servidor/`)
```bash
cd qrypta/servidor
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt  # incluye pytest-asyncio, oqs
pytest tests -q
# Arranque local:
bash ../../scripts/server_ctl.sh start
```

### Núcleo Cripto (`qrypta/nucleo_crypto/`)
```bash
cd qrypta/nucleo_crypto
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests -q
```

### Cliente Web (`qrypta/cliente_web/`)
```bash
cd qrypta/cliente_web
npm install
npm run dev          # desarrollo
npm run build        # producción
npm run test:run     # tests
```

### Cliente Escritorio (`qrypta/cliente_escritorio/`)
```bash
cd qrypta/cliente_escritorio
npm install
npm run dev          # desarrollo (Vite + Tauri)
npm run build        # build frontend
cargo tauri dev      # desarrollo completo (requiere Rust)
cargo tauri build    # binarios nativos
```

### Cliente Móvil (`qrypta/cliente_movil/`)
```bash
cd qrypta/cliente_movil
flutter pub get
flutter test         # tests
flutter run          # desarrollo (requiere device/emulador)
flutter build apk    # Android release (requiere Android SDK)
flutter build ios    # iOS release (requiere macOS)
```

---

## GitFlow - Flujo de Trabajo

### Ramas Principales
| Rama | Propósito | Protección |
|------|-----------|------------|
| `main` | Versiones estables, releases | Branch protection + CI obligatorio |
| `develop` | Integración continua | CI obligatorio |

### Ramas de Trabajo
| Prefijo | Uso | Desde | Hacia |
|---------|-----|-------|-------|
| `feature/*` | Nueva funcionalidad | `develop` | `develop` (PR) |
| `release/x.y.z` | Preparación release | `develop` | `main` + `develop` (PR) |
| `hotfix/*` | Corrección crítica prod | `main` | `main` + `develop` (PR) |

### Flujo Estándar
```bash
# 1. Nueva feature
git checkout develop
git pull origin develop
git checkout -b feature/nombre-funcionalidad

# 2. Desarrollar + commits (formato: [tipo]: descripción)
git commit -m "feat: agregar verificación de alias"
git commit -m "fix: corregir bug en exportación de backup"
git commit -m "docs: actualizar README"

# 3. Push + PR a develop
git push origin feature/nombre-funcionalidad
# Crear PR en GitHub: feature/* → develop

# 4. CI pasa → Merge (squash o merge commit)

# 5. Release
git checkout develop
git pull origin develop
git checkout -b release/1.0.0
# Ajustes finales, version bump
git push origin release/1.0.0
# PR: release/* → main
# Merge a main → Tag automático v1.0.0 → release.yml dispara Docker publish
# Back-merge: main → develop
```

### Convención de Commits (Conventional Commits)
```
feat:     Nueva funcionalidad
fix:      Corrección de bug
docs:     Documentación
style:    Formato (sin cambio lógico)
refactor: Refactor interno
test:     Tests
chore:    Mantenimiento (deps, configs)
ci:       CI/CD
```

---

## Guía de Estilo (Referencia Rápida)

Ver `ESTYLEGUIDE.md` para detalle completo.

| Elemento | Convención |
|----------|------------|
| Variables | camelCase (`clavePrivadaKyber`) |
| Clases/Módulos | PascalCase (`GestorAlias`) |
| Constantes | MAYÚSCULAS_CON_GUIONES (`MAX_INTENTOS`) |
| Archivos | snake_case (`registro_verificacion.py`) |
| Commits | `[tipo]: descripción` en español |
| Comentarios | Español, lógica de módulo |
| Funciones | Máx. 30 líneas |

---

## Scripts Útiles (Raíz del Proyecto)

```bash
# Validar clientes para beta
./scripts/beta_clients_ready.sh

# Control servidor local
./scripts/server_ctl.sh start|stop|restart|status|logs

# Actualizar dependencias
./scripts/update.sh

# Flujo GitFlow asistido
./scripts/github_flow.sh
```

---

## CI/CD - Validación Local Pre-Push

```bash
# Tests núcleo + servidor (rápido)
cd qrypta/nucleo_crypto && pytest tests -q
cd ../../qrypta/servidor && pytest tests -q

# Tests clientes (requiere toolchains)
cd ../../qrypta/cliente_web && npm run test:run
cd ../../qrypta/cliente_escritorio && npm run test:run
cd ../../qrypta/cliente_movil && flutter test

# Build Docker servidor
docker build -t bastion-servidor -f qrypta/servidor/Dockerfile qrypta
```

---

## Troubleshooting Común

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError: oqs` | Instalar liboqs + `pip install oqs` |
| `cargo: not found` | `source "$HOME/.cargo/env"` o reinstalar rustup |
| `flutter: command not found` | Añadir Flutter al PATH o `flutter doctor` |
| `Android SDK not found` | Configurar `ANDROID_HOME` y `flutter config --android-sdk` |
| Tests nucleo fallan en CI | Verificar que workflow instala `oqs` antes de `pytest` |
| Docker build falla | Verificar `Dockerfile` context path (`qrypta/` no `qrypta/servidor/`) |

---

## Documentación Relacionada

| Archivo | Propósito |
|---------|-----------|
| `PLAN.md` | Roadmap maestro + Beta Sprint Plan |
| `ARCHITECTURE.md` | Arquitectura, decisiones tech, políticas |
| `BETA_READINESS_REPORT.md` | Estado actual para beta test |
| `ESTYLEGUIDE.md` | Guía estilo completa |
| `archive/PLAN_FASE13_ADMIN.md` | Histórico detallado Fase 13 |