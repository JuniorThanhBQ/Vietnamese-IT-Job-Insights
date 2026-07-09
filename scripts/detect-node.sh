#!/bin/bash
set -euo pipefail

if [ -f "package.json" ]; then
  echo "Node project detected."
  echo "detected=true" >> "$GITHUB_OUTPUT"

  if [ -f "yarn.lock" ]; then
    echo "manager=yarn" >> "$GITHUB_OUTPUT"
    echo "command=yarn install --frozen-lockfile" >> "$GITHUB_OUTPUT"
    echo "runner=yarn run" >> "$GITHUB_OUTPUT"
  elif [ -f "pnpm-lock.yaml" ]; then
    echo "manager=pnpm" >> "$GITHUB_OUTPUT"
    echo "command=pnpm install --frozen-lockfile" >> "$GITHUB_OUTPUT"
    echo "runner=pnpm run" >> "$GITHUB_OUTPUT"
  else
    echo "manager=npm" >> "$GITHUB_OUTPUT"
    echo "command=npm ci" >> "$GITHUB_OUTPUT"
    echo "runner=npm run" >> "$GITHUB_OUTPUT"
  fi
else
  echo "No JavaScript/TypeScript source detected. Skipping ESLint."
  echo "detected=false" >> "$GITHUB_OUTPUT"
fi
