#!/bin/bash
set -euo pipefail

echo "Installing Checkov for Docker Compose linting..."
pip install --upgrade pip checkov > /dev/null

echo "Running Compose lint for dangerous configurations..."

for file in $COMPOSE_FILES; do
  echo "--- Linting $file ---"
  checkov --file "$file" --framework docker_compose --compact || {
    echo "::error file=$file::Compose Lint phát hiện cấu hình nguy hiểm/thiếu bảo mật trong $file. Vui lòng kiểm tra log để biết chi tiết và cách khắc phục."
    exit 1
  }
done

echo "✅ Compose lint passed."
