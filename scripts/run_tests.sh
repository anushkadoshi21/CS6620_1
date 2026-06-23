#!/usr/bin/env bash
#
# run_tests.sh — build and run the test container.
# Exits 0 if all tests pass, non-zero if any test fails.

set -euo pipefail

# Run from the repo root regardless of where the script is invoked from,
# so the Docker build context (".") always points at the project root.
cd "$(dirname "$0")/.."

# --- Config -------
IMAGE_NAME="myapp-tests:latest"
DOCKERFILE="Dockerfile.tests"

# --- Build -------
# Docker build the test image.
docker build -f "$DOCKERFILE" -t "$IMAGE_NAME" .

# --- Run ----------
# Docker run the test image.
#   - --rm so the stopped container is cleaned up automatically

# With `set -e`, a non-zero exit from docker run will end this script with that same non-zero code automatically — which is exactly the pass/fail signal CI workflow needs. 

docker run --rm "$IMAGE_NAME"