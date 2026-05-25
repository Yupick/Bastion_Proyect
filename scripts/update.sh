#!/usr/bin/env bash
set -euo pipefail

# Script de actualizacion del repo.
# Permite elegir origen: master o develop.
# Ejemplos:
#   bash scripts/update.sh --from-master --autostash
#   bash scripts/update.sh --from-develop --merge-current --autostash

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SOURCE_BRANCH=""   # master|develop
MODE="none"        # none|merge|rebase
AUTOSTASH="false"

usage() {
  echo "Uso: $0 [--from-master|--from-develop] [--merge-current|--rebase-current] [--autostash]"
  echo "  --from-master    Actualiza desde origin/master (fallback a origin/main si master no existe)."
  echo "  --from-develop   Actualiza desde origin/develop."
  echo "  --merge-current  Integra la rama origen en la rama actual via merge."
  echo "  --rebase-current Integra la rama origen en la rama actual via rebase."
  echo "  --autostash      Guarda temporalmente cambios locales y los restaura al final."
}

resolve_source_branch() {
  local requested="$1"

  if [[ "$requested" == "master" ]]; then
    if git ls-remote --exit-code --heads origin master >/dev/null 2>&1; then
      echo "master"
      return
    fi
    if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
      echo "main"
      return
    fi
    echo ""
    return
  fi

  if [[ "$requested" == "develop" ]]; then
    if git ls-remote --exit-code --heads origin develop >/dev/null 2>&1; then
      echo "develop"
      return
    fi
    echo ""
    return
  fi

  echo ""
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --from-master)
      SOURCE_BRANCH="master"
      shift
      ;;
    --from-develop)
      SOURCE_BRANCH="develop"
      shift
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
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Argumento no reconocido: $1"
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$SOURCE_BRANCH" ]]; then
  echo "ERROR: Debes especificar --from-master o --from-develop"
  usage
  exit 1
fi

CURRENT_BRANCH="$(git branch --show-current)"
RESOLVED_SOURCE="$(resolve_source_branch "$SOURCE_BRANCH")"
STASH_NAME="autostash-update-$(date +%s)"

if [[ -z "$RESOLVED_SOURCE" ]]; then
  echo "ERROR: No se encontro origin/$SOURCE_BRANCH"
  if [[ "$SOURCE_BRANCH" == "master" ]]; then
    echo "Nota: tambien se intento origin/main y tampoco existe."
  fi
  exit 1
fi

if [[ "$SOURCE_BRANCH" == "master" && "$RESOLVED_SOURCE" == "main" ]]; then
  echo "Aviso: origin/master no existe. Usando origin/main."
fi

SOURCE_BRANCH="$RESOLVED_SOURCE"

if [[ -n "$(git status --porcelain)" ]]; then
  if [[ "$AUTOSTASH" == "true" ]]; then
    echo "Hay cambios locales: aplicando autostash temporal"
    git stash push -u -m "$STASH_NAME" >/dev/null
  else
    echo "ERROR: Hay cambios locales sin commit. Usa --autostash o commitea antes."
    exit 1
  fi
fi

echo "Fetch origin/$SOURCE_BRANCH..."
git fetch origin "$SOURCE_BRANCH"

if git show-ref --verify --quiet "refs/heads/$SOURCE_BRANCH"; then
  echo "Actualizando rama local $SOURCE_BRANCH"
  git checkout "$SOURCE_BRANCH"
  git merge --ff-only "origin/$SOURCE_BRANCH"
else
  echo "Creando rama local $SOURCE_BRANCH desde origin/$SOURCE_BRANCH"
  git checkout -b "$SOURCE_BRANCH" "origin/$SOURCE_BRANCH"
fi

if [[ "$CURRENT_BRANCH" != "$SOURCE_BRANCH" ]]; then
  git checkout "$CURRENT_BRANCH"
fi

if [[ "$MODE" == "merge" && "$CURRENT_BRANCH" != "$SOURCE_BRANCH" ]]; then
  echo "Integrando $SOURCE_BRANCH en $CURRENT_BRANCH via merge"
  git merge "$SOURCE_BRANCH"
elif [[ "$MODE" == "rebase" && "$CURRENT_BRANCH" != "$SOURCE_BRANCH" ]]; then
  echo "Integrando $SOURCE_BRANCH en $CURRENT_BRANCH via rebase"
  git rebase "$SOURCE_BRANCH"
else
  echo "Rama local $SOURCE_BRANCH actualizada. Sin integracion en rama actual."
fi

echo "Estado final:"
git --no-pager log --oneline -5

if git stash list | grep -q "$STASH_NAME"; then
  echo "Restaurando cambios stasheados"
  git stash pop >/dev/null || {
    echo "Aviso: conflicto al restaurar stash. Revisa git status."
  }
fi
