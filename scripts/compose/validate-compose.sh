#!/bin/bash
set -euo pipefail

echo "Validating Docker Compose syntax..."

for file in $COMPOSE_FILES; do
  echo "Checking syntax for $file..."
  if ! docker compose -f "$file" config --quiet; then
    echo "::error file=$file::Syntax error in file $file"
    exit 1
  fi
  echo "✅ $file syntax is valid."
done
