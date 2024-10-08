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

add_all() {
  if cd "$PROJECT_ROOT"; then
    git add -A . && pre-commit run --all-files
    return $?
  fi
}

add_all_and_commit() {
  local msg="$*"
  msg=$(echo -en "$msg" | tr -s '[:blank:]')
  if cd "$PROJECT_ROOT"; then
    { add_all || add_all; } && git add -A . &&
      git commit -m "$msg"
  fi
}

if [[ $# -ge 1 ]]; then
  case "$1" in
    init) init_pre_commit ;;
    run) pre-commit run --all-files ;;
    sync) sync_env ;;
    add-all) add_all ;;
    commit-all) add_all_and_commit "${@:2}" ;;
  esac
fi
