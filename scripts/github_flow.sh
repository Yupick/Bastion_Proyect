#!/usr/bin/env bash
set -euo pipefail

# Flujo GitHub end-to-end: commit/push, PR, merge, tag y release.
# Requiere: git + gh autenticado con scope repo.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

BASE_BRANCH="master"
TAG=""
RELEASE_TITLE=""
PR_TITLE=""
PR_BODY=""
COMMIT_MSG="chore: update project"
AUTO_COMMIT="false"
MERGE_STRATEGY="merge" # merge | squash | rebase

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

usage() {
  echo "Uso: $0 --tag vX.Y.Z [opciones]"
  echo "Opciones:"
  echo "  --base master|main"
  echo "  --tag vX.Y.Z"
  echo "  --release-title \"Release vX.Y.Z\""
  echo "  --pr-title \"Titulo PR\""
  echo "  --pr-body \"Descripcion PR\""
  echo "  --auto-commit"
  echo "  --commit-msg \"mensaje commit\""
  echo "  --merge-strategy merge|squash|rebase"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base)
      BASE_BRANCH="$2"
      shift 2
      ;;
    --tag)
      TAG="$2"
      shift 2
      ;;
    --release-title)
      RELEASE_TITLE="$2"
      shift 2
      ;;
    --pr-title)
      PR_TITLE="$2"
      shift 2
      ;;
    --pr-body)
      PR_BODY="$2"
      shift 2
      ;;
    --auto-commit)
      AUTO_COMMIT="true"
      shift
      ;;
    --commit-msg)
      COMMIT_MSG="$2"
      shift 2
      ;;
    --merge-strategy)
      MERGE_STRATEGY="$2"
      shift 2
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

if [[ -z "$TAG" ]]; then
  echo "ERROR: Debes indicar --tag"
  usage
  exit 1
fi

RESOLVED_BASE="$(resolve_base_branch "$BASE_BRANCH")"
if [[ -z "$RESOLVED_BASE" ]]; then
  echo "ERROR: No se encontro rama base en origin (master/main/develop)."
  exit 1
fi
if [[ "$RESOLVED_BASE" != "$BASE_BRANCH" ]]; then
  echo "Aviso: origin/$BASE_BRANCH no existe. Usando origin/$RESOLVED_BASE."
fi
BASE_BRANCH="$RESOLVED_BASE"

CURRENT_BRANCH="$(git branch --show-current)"
if [[ "$CURRENT_BRANCH" == "$BASE_BRANCH" ]]; then
  echo "ERROR: Ejecuta este flujo desde una rama feature, no desde $BASE_BRANCH"
  exit 1
fi

if [[ "$AUTO_COMMIT" == "true" ]]; then
  if [[ -n "$(git status --porcelain)" ]]; then
    git add -A
    git commit -m "$COMMIT_MSG"
  fi
else
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: Hay cambios sin commit. Usa --auto-commit o commitea manualmente."
    git status --short
    exit 1
  fi
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh no esta autenticado. Ejecuta: gh auth login"
  exit 1
fi

git fetch origin "$BASE_BRANCH"
git push -u origin "$CURRENT_BRANCH"

if [[ -z "$PR_TITLE" ]]; then
  PR_TITLE="Merge $CURRENT_BRANCH into $BASE_BRANCH"
fi
if [[ -z "$PR_BODY" ]]; then
  PR_BODY="PR automatica generada por scripts/github_flow.sh"
fi

if gh pr view "$CURRENT_BRANCH" >/dev/null 2>&1; then
  echo "PR ya existe para rama $CURRENT_BRANCH"
else
  gh pr create --base "$BASE_BRANCH" --head "$CURRENT_BRANCH" --title "$PR_TITLE" --body "$PR_BODY"
fi

PR_NUMBER="$(gh pr view "$CURRENT_BRANCH" --json number --jq .number)"
echo "PR #$PR_NUMBER listo"

case "$MERGE_STRATEGY" in
  merge)
    gh pr merge "$PR_NUMBER" --merge --delete-branch
    ;;
  squash)
    gh pr merge "$PR_NUMBER" --squash --delete-branch
    ;;
  rebase)
    gh pr merge "$PR_NUMBER" --rebase --delete-branch
    ;;
  *)
    echo "ERROR: merge-strategy invalida: $MERGE_STRATEGY"
    exit 1
    ;;
esac

# Asegura base actualizada localmente
if git show-ref --verify --quiet "refs/heads/$BASE_BRANCH"; then
  git checkout "$BASE_BRANCH"
else
  git checkout -b "$BASE_BRANCH" "origin/$BASE_BRANCH"
fi
git pull --ff-only origin "$BASE_BRANCH"

# Tag
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Tag ya existe localmente: $TAG"
else
  git tag -a "$TAG" -m "$TAG"
fi

git push origin "$TAG"

if [[ -z "$RELEASE_TITLE" ]]; then
  RELEASE_TITLE="Release $TAG"
fi

if gh release view "$TAG" >/dev/null 2>&1; then
  echo "Release ya existe para $TAG"
else
  gh release create "$TAG" --title "$RELEASE_TITLE" --notes "Release automatizada para $TAG"
fi

echo "Flujo completado: merge + tag + release"
