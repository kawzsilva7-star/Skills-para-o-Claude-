#!/usr/bin/env bash
# Atalho do sistema de cortes (Mac/Linux): ./cortes.sh <comando>
SKILL="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$SKILL" PYTHONIOENCODING=utf-8
PY="$SKILL/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3 || command -v python)"
exec "$PY" -m sistema_cortes "$@"
