#!/usr/bin/env bash
set -euo pipefail

# Control unificado del servidor Qrypta: start, stop, restart, status, logs
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$REPO_ROOT/qrypta"
LOG_DIR="$APP_DIR/servidor/logs"
PID_FILE="$LOG_DIR/uvicorn.pid"
LOG_FILE="$LOG_DIR/uvicorn.log"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
RELOAD="${RELOAD:-false}"

if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
else
  PYTHON_BIN="$(command -v python3)"
fi

mkdir -p "$LOG_DIR"

is_running() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE")"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

start_server() {
  if is_running; then
    echo "Servidor ya esta en ejecucion (PID $(cat "$PID_FILE"))."
    return 0
  fi

  local reload_flag=""
  if [[ "$RELOAD" == "true" ]]; then
    reload_flag="--reload"
  fi

  echo "Iniciando servidor en $HOST:$PORT"
  (
    cd "$APP_DIR"
    nohup "$PYTHON_BIN" -m uvicorn servidor.main:app --host "$HOST" --port "$PORT" $reload_flag >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
  )

  sleep 1
  if is_running; then
    echo "Servidor iniciado (PID $(cat "$PID_FILE"))."
    echo "Log: $LOG_FILE"
  else
    echo "No se pudo iniciar el servidor. Revisa logs: $LOG_FILE"
    exit 1
  fi
}

stop_server() {
  if ! is_running; then
    echo "Servidor no esta en ejecucion."
    rm -f "$PID_FILE"
    return 0
  fi

  local pid
  pid="$(cat "$PID_FILE")"
  echo "Deteniendo servidor (PID $pid)"
  kill "$pid" 2>/dev/null || true

  for _ in {1..20}; do
    if kill -0 "$pid" 2>/dev/null; then
      sleep 0.2
    else
      rm -f "$PID_FILE"
      echo "Servidor detenido."
      return 0
    fi
  done

  echo "Forzando detencion (SIGKILL) del PID $pid"
  kill -9 "$pid" 2>/dev/null || true
  rm -f "$PID_FILE"
}

status_server() {
  if is_running; then
    echo "RUNNING PID=$(cat "$PID_FILE")"
  else
    echo "STOPPED"
  fi
}

show_logs() {
  local lines="${2:-120}"
  if [[ ! -f "$LOG_FILE" ]]; then
    echo "No existe log aun: $LOG_FILE"
    return 0
  fi

  if [[ "${3:-}" == "follow" || "${2:-}" == "follow" ]]; then
    echo "Siguiendo logs en vivo: $LOG_FILE"
    tail -n "$lines" -f "$LOG_FILE"
  else
    tail -n "$lines" "$LOG_FILE"
  fi
}

case "${1:-}" in
  start)
    start_server
    ;;
  stop)
    stop_server
    ;;
  restart)
    stop_server
    start_server
    ;;
  status)
    status_server
    ;;
  logs)
    show_logs "$@"
    ;;
  *)
    echo "Uso: $0 {start|stop|restart|status|logs [lineas]|logs [lineas] follow}"
    exit 1
    ;;
esac
