#!/bin/bash
set -euo pipefail

echo "Running Trivy Scan to enforce security rules and output to logs..."
trivy fs . --scanners vuln,secret,misconfig \
  --severity HIGH,CRITICAL \
  --format table \
  --exit-code 1 || {
    echo "::error::Trivy scan detected HIGH/CRITICAL vulnerabilities or misconfigurations. See the results above for remediation guidance."
    exit 1
  }
echo "✅ Trivy scan passed."
