#!/bin/bash
set -euo pipefail

COMPOSE_FILES=$(find . -type f \( -name "docker-compose.yml" -o -name "docker-compose.yaml" -o -name "compose.yml" -o -name "compose.yaml" \) -not -path "*/\.*" -not -path "*/node_modules/*")

if [ -z "$COMPOSE_FILES" ]; then
  echo "No Docker Compose file detected."
  echo "Skipping Compose validation."
  echo "has_compose=false" >> "$GITHUB_OUTPUT"
else
  echo "Docker Compose files detected:"
  echo "$COMPOSE_FILES"
  echo "has_compose=true" >> "$GITHUB_OUTPUT"

  FILES_INLINE=$(echo "$COMPOSE_FILES" | tr '\n' ' ')
  echo "compose_files=$FILES_INLINE" >> "$GITHUB_OUTPUT"
fi
