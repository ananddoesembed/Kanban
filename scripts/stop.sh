#!/usr/bin/env sh
set -eu

CONTAINER_NAME="pm-mvp"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required but was not found on PATH." >&2
  exit 1
fi

docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

echo "Stopped $CONTAINER_NAME"