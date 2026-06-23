#!/usr/bin/env bash
#
# run_api.sh — build and run the REST API container.
# The API stays running in the foreground until manually stopped (Ctrl-C).

set -euo pipefail

# Run from the repo root regardless of where the script is invoked from,
# so the Docker build context (".") always points at the project root.
cd "$(dirname "$0")/.."

# --- Config -----------
IMAGE_NAME="myapp-api:latest"
DOCKERFILE="Dockerfile.api"
PORT="8000"

# --- Build ------------
# Docker build the API image.
docker build -f "$DOCKERFILE" -t "$IMAGE_NAME" .


# --- Run --------------
# Docker run the API image.
#   - --rm so the stopped container is cleaned up automatically
#   - -p "$PORT:$PORT" so the API is accessible on localhost:$PORT
docker run --rm -p "$PORT:$PORT" "$IMAGE_NAME"
