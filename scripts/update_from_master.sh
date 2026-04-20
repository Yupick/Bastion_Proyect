#!/usr/bin/env bash
set -euo pipefail

# Actualiza el repositorio con cambios de origin/master y opcionalmente integra en la rama actual.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

BASE_BRANCH="master"
MODE="none"  # none | merge | rebase
AUTOSTASH="false"

resolve_base_branch() {
  local requested="$1"
  if git ls-remote --exit-code --heads origin "$requested" >/dev/null 2>&1; then
    echo "$requested"
    return
  fi
  for candidate in master main develop; do
    if git ls-remote --exit-code --heads origin "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return
    fi
  done
  echo ""
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base)
      BASE_BRANCH="$2"
      shift 2
      ;;
    --merge-current)
      MODE="merge"
      shift
      ;;
    --rebase-current)
      MODE="rebase"
      shift
      ;;
    --autostash)
      AUTOSTASH="true"
      shift
      ;;
    *)
      echo "Argumento no reconocido: $1"
      echo "Uso: $0 [--base master] [--merge-current|--rebase-current]"
      exit 1
      ;;
  esac
done

CURRENT_BRANCH="$(git branch --show-current)"
RESOLVED_BASE="$(resolve_base_branch "$BASE_BRANCH")"
STASH_NAME="autostash-update-$(date +%s)"

if [[ -z "$RESOLVED_BASE" ]]; then
  echo "ERROR: No se encontro rama base en origin (master/main/develop)."
  exit 1
fi

if [[ "$RESOLVED_BASE" != "$BASE_BRANCH" ]]; then
  echo "Aviso: origin/$BASE_BRANCH no existe. Usando origin/$RESOLVED_BASE."
fi

BASE_BRANCH="$RESOLVED_BASE"

if [[ -n "$(git status --porcelain)" ]]; then
  if [[ "$AUTOSTASH" == "true" ]]; then
    echo "Hay cambios locales: aplicando autostash temporal"
    git stash push -u -m "$STASH_NAME" >/dev/null
  else
    echo "ERROR: Hay cambios locales sin commit. Usa --autostash o commitea antes."
    exit 1
  fi
fi

echo "Fetch origin..."
git fetch origin "$BASE_BRANCH"

if git show-ref --verify --quiet "refs/heads/$BASE_BRANCH"; then
  echo "Actualizando rama local $BASE_BRANCH"
  git checkout "$BASE_BRANCH"
  git merge --ff-only "origin/$BASE_BRANCH"
else
  echo "Creando rama local $BASE_BRANCH desde origin/$BASE_BRANCH"
  git checkout -b "$BASE_BRANCH" "origin/$BASE_BRANCH"
fi

if [[ "$CURRENT_BRANCH" != "$BASE_BRANCH" ]]; then
  git checkout "$CURRENT_BRANCH"
fi

if [[ "$MODE" == "merge" && "$CURRENT_BRANCH" != "$BASE_BRANCH" ]]; then
  echo "Integrando $BASE_BRANCH en $CURRENT_BRANCH via merge"
  git merge "$BASE_BRANCH"
elif [[ "$MODE" == "rebase" && "$CURRENT_BRANCH" != "$BASE_BRANCH" ]]; then
  echo "Integrando $BASE_BRANCH en $CURRENT_BRANCH via rebase"
  git rebase "$BASE_BRANCH"
else
  echo "Rama local $BASE_BRANCH actualizada. Sin integracion en rama actual."
fi

echo "Estado final:"
git --no-pager log --oneline -5

if git stash list | grep -q "$STASH_NAME"; then
  echo "Restaurando cambios stasheados"
  git stash pop >/dev/null || {
    echo "Aviso: conflicto al restaurar stash. Revisa git status."
  }
fi
