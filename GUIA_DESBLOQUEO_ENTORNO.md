# Guia de desbloqueo de entorno (manual)

Este entorno tiene bloqueo de subcomandos de descarga (`curl`/`wget`) y no dispone de `sudo` en la sesion actual.

## 1) Rust/Cargo para Tauri (13c)

Ejecutar con un usuario con privilegios:

```bash
sudo apt update
sudo apt install -y cargo rustc
cargo --version
```

Alternativa (rustup):

```bash
curl https://sh.rustup.rs -sSf | sh -s -- -y
source "$HOME/.cargo/env"
cargo --version
```

## 2) Android SDK para Flutter release (13a.8)

Opcion recomendada:

1. Instalar Android Studio.
2. Instalar Android SDK, Platform-tools y Build-tools desde SDK Manager.
3. Configurar Flutter:

```bash
flutter config --android-sdk "$HOME/Android/Sdk"
flutter doctor --android-licenses
flutter doctor -v
```

Opcion CLI (si hay permisos de descarga):

```bash
mkdir -p "$HOME/Android/Sdk/cmdline-tools"
# Descargar commandline-tools de Android y descomprimir en:
# $HOME/Android/Sdk/cmdline-tools/latest

export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
flutter config --android-sdk "$ANDROID_HOME"
flutter doctor -v
```

## 3) iOS IPA

`flutter build ipa` solo se puede ejecutar en macOS con Xcode.

## 4) Integration tests Flutter

Requiere emulador/dispositivo Android o iOS compatible para `integration_test`.
