#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python training/train_model.py
python training/model_audit.py
