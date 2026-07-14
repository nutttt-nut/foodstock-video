#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rsync -av root@152.42.197.67:/opt/foodstock-editor/data/ "$ROOT/data/"
