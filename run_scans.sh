#!/usr/bin/env bash
set -e

echo "Running flake8..."
pip install flake8 bandit pip-audit
flake8 app || true

echo "Running bandit..."
bandit -r app -f json -o bandit-report.json || true

echo "Running pip-audit..."
pip-audit --require-allowlist --format=json --output=pip-audit.json || true

echo "Local scans complete. Reports: bandit-report.json, pip-audit.json"
