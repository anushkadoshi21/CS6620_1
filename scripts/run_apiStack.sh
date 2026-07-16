#!/bin/bash
set -euo pipefail

# Run from the repo root regardless of where the script is invoked from,
# so the Docker build context (".") always points at the project root.
cd "$(dirname "$0")/.."

echo "Starting stack (Ctrl+C to stop)..."
docker compose -f compose.apiStack.yml up --build