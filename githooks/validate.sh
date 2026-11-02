#!/bin/sh
set -eu

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root/backend"

if [ -x ".venv/Scripts/python.exe" ]; then
    PYTHON="./.venv/Scripts/python.exe"
elif [ -x ".venv/bin/python" ]; then
    PYTHON="./.venv/bin/python"
else
    PYTHON="python"
fi

case "${1:-}" in
    pre-commit)
        "$PYTHON" -m ruff check app tests
        "$PYTHON" -m ruff format --check app tests
        "$PYTHON" -m pytest -q
        ;;
    pre-push)
        "$PYTHON" -m pytest -q
        ;;
    *)
        printf '%s\n' "Uso: validate.sh pre-commit|pre-push" >&2
        exit 2
        ;;
esac
