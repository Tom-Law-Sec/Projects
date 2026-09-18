#!/usr/bin/env bash
# Run from any directory. The image lock is used automatically once present.
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -f .env ]]; then
  echo 'Missing .env: run python3 ../../scripts/init_env.py first.' >&2
  exit 2
fi
args=(-f compose.yaml)
[[ ! -f compose.images.yaml ]] || args+=(-f compose.images.yaml)
exec docker compose "${args[@]}" "$@"
