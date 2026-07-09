#!/bin/bash
set -euo pipefail

echo "Running Trivy Scan to enforce security rules and output to logs..."
trivy fs . --scanners vuln,secret,misconfig \
  --severity HIGH,CRITICAL \
  --format table \
  --exit-code 1 || {
    echo "::error::Trivy scan phát hiện lỗ hổng/cấu hình sai mức độ HIGH/CRITICAL. Xem bảng kết quả bên trên để tìm cách khắc phục."
    exit 1
  }
echo "✅ Trivy scan passed."
