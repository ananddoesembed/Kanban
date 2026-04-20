#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
IMAGE_NAME="pm-mvp"
CONTAINER_NAME="pm-mvp"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required but was not found on PATH." >&2
  exit 1
fi

docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
docker build -t "$IMAGE_NAME" "$REPO_ROOT"

if [ -f "$REPO_ROOT/.env" ]; then
  docker run --detach --name "$CONTAINER_NAME" --env-file "$REPO_ROOT/.env" -p 8000:8000 "$IMAGE_NAME" >/dev/null
else
  docker run --detach --name "$CONTAINER_NAME" -p 8000:8000 "$IMAGE_NAME" >/dev/null
fi

echo "Started http://localhost:8000"