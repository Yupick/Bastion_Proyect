#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_FILE="$ROOT_DIR/qrypta/docs/BETA_CLIENTS_READINESS.md"
DATE_UTC="$(date -u +"%Y-%m-%d %H:%M:%S UTC")"

WEB_STATUS="PENDING"
DESKTOP_STATUS="PENDING"
MOBILE_STATUS="PENDING"

run_step() {
  local label="$1"
  shift

  echo "[beta] $label"
  if "$@"; then
    echo "[beta] OK: $label"
    return 0
  fi

  echo "[beta] ERROR: $label"
  return 1
}

run_in_dir() {
  local dir="$1"
  shift

  pushd "$dir" >/dev/null
  "$@"
  local exit_code=$?
  popd >/dev/null
  return $exit_code
}

if run_step "Cliente web: tests" run_in_dir "$ROOT_DIR/qrypta/cliente_web" npm run test:run \
  && run_step "Cliente web: build" run_in_dir "$ROOT_DIR/qrypta/cliente_web" npm run build; then
  WEB_STATUS="PASS"
else
  WEB_STATUS="FAIL"
fi

if run_step "Cliente escritorio: tests" run_in_dir "$ROOT_DIR/qrypta/cliente_escritorio" npm run test:run \
  && run_step "Cliente escritorio: build" run_in_dir "$ROOT_DIR/qrypta/cliente_escritorio" npm run build; then
  DESKTOP_STATUS="PASS"
else
  DESKTOP_STATUS="FAIL"
fi

if command -v flutter >/dev/null 2>&1; then
  if run_step "Cliente movil: flutter test" run_in_dir "$ROOT_DIR/qrypta/cliente_movil" flutter test; then
    MOBILE_STATUS="PASS"
  else
    MOBILE_STATUS="FAIL"
  fi
else
  MOBILE_STATUS="SKIP (flutter no disponible)"
fi

cat > "$REPORT_FILE" << EOF
# Beta Clients Readiness

Generado: $DATE_UTC

## Resumen
- Cliente web: $WEB_STATUS
- Cliente escritorio: $DESKTOP_STATUS
- Cliente movil: $MOBILE_STATUS

## Criterio
- PASS: pruebas y build (cuando aplique) ejecutados correctamente.
- FAIL: hay errores de pruebas/build que bloquean beta.
- SKIP: entorno sin toolchain requerido.

## Comando recomendado
- scripts/beta_clients_ready.sh
EOF

if [[ "$WEB_STATUS" == "PASS" && "$DESKTOP_STATUS" == "PASS" && "$MOBILE_STATUS" == "PASS" ]]; then
  echo "[beta] Beta clients gate: PASS"
  exit 0
fi

if [[ "$MOBILE_STATUS" == "SKIP (flutter no disponible)" && "$WEB_STATUS" == "PASS" && "$DESKTOP_STATUS" == "PASS" ]]; then
  echo "[beta] Beta clients gate: PARTIAL (movil no validado en este entorno)"
  exit 0
fi

echo "[beta] Beta clients gate: FAIL"
exit 1
