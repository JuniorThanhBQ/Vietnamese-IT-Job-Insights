#!/bin/bash
set -euo pipefail

echo "Generating Trivy SARIF report for entire repository..."
trivy fs . --scanners vuln,secret,misconfig \
  --severity HIGH,CRITICAL \
  --format sarif \
  --output trivy-results.sarif \
  --exit-code 0