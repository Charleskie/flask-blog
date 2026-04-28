#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export FLASK_ENV="${FLASK_ENV:-production}"
export PYTHONUNBUFFERED=1

exec python3 -m app.tasks.cli scheduler
