#!/bin/bash
set -euo pipefail

echo "Installing Checkov for Docker Compose linting..."
pip install --upgrade pip checkov > /dev/null

echo "Running Compose lint for dangerous configurations..."

for file in $COMPOSE_FILES; do
  echo "--- Linting $file ---"
  checkov --file "$file" --framework docker_compose --compact || {
    echo "::error file=$file::Compose Lint detected dangerous or insecure configuration in $file. Please check the logs for details and remediation steps."
    exit 1
  }
done

echo "✅ Compose lint passed."
