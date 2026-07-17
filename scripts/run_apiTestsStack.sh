#!/bin/bash
set -euo pipefail

# Run from the repo root regardless of where the script is invoked from,
# so the Docker build context (".") always points at the project root.
cd "$(dirname "$0")/.."

echo "Starting stack (Ctrl+C to stop)..."

#exit with tests service/container exit code and stop all other containers in the stack
docker compose -f compose.apiTest.yml up --build --exit-code-from tests --abort-on-container-exit