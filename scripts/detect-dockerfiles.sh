#!/bin/bash
set -euo pipefail

DOCKERFILES=$(find . -type f -name "Dockerfile*" -not -path "*/\.*" -not -path "*/node_modules/*")

if [ -z "$DOCKERFILES" ]; then
  echo "No Dockerfiles detected."
  echo "has_dockerfile=false" >> "$GITHUB_OUTPUT"
else
  echo "Dockerfiles detected:"
  echo "$DOCKERFILES"
  echo "has_dockerfile=true" >> "$GITHUB_OUTPUT"
fi