#!/usr/bin/env bash

HERE="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$HERE")"

sync_env() {
  # shellcheck source=../.venv/bin/activate
  rye sync && \. "$PROJECT_ROOT/.venv/bin/activate"
}

init_pre_commit() {
  echo "Initializing pre-commit ..." && {
    pre-commit autoupdate
    pre-commit install --install-hooks \
      --hook-type commit-msg --hook-type pre-push
  } && echo "... Done!"
}

if [[ $# -eq 1 ]]; then
  case "$1" in
    init) init_pre_commit ;;
    run) pre-commit run --all-files ;;
    sync) sync_env ;;
  esac
fi
