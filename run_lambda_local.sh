#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PYTHONPATH="$ROOT/lambda-code/layers/requests_layer/python:$ROOT/lambda-code/layers/shared_utils_layer/python${PYTHONPATH:+:$PYTHONPATH}"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <handler_file.py> [args...]"
  echo "Example: $0 lambda-code/European_Research_Council/handler.py"
  exit 1
fi

HANDLER="$1"
shift

exec /opt/homebrew/bin/python3 "$ROOT/$HANDLER" "$@"
