#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mode="${1:-}"
dryrun=false
if [[ "${2:-}" == "--dry-run" ]]; then dryrun=true; fi

next_version() {
  local max=0 f n
  shopt -s nullglob
  for f in foodstock-loop-v*.mp4; do
    n=$(echo "$f" | sed -E 's/foodstock-loop-v([0-9]+).*/\1/')
    if [[ "$n" =~ ^[0-9]+$ ]] && (( n > max )); then max=$n; fi
  done
  shopt -u nullglob
  echo $(( max + 1 ))
}

case "$mode" in
  preview)
    echo "==> generate.py"
    python3 generate.py
    echo "==> render preview (fps 15, quality draft)"
    npx hyperframes render . --fps 15 --quality draft --output preview.mp4
    echo "==> done: preview.mp4"
    ;;

  final)
    ver=$(next_version)
    outname="foodstock-loop-v${ver}-$(date +%Y-%m-%d).mp4"

    if $dryrun; then
      echo "$outname"
      exit 0
    fi

    echo "==> pull data from VPS"
    bash scripts/pull-editor-data.sh
    echo "==> generate.py"
    python3 generate.py
    echo "==> render final (fps 30)"
    npx hyperframes render . --fps 30 --output "$outname"
    echo "==> done: $outname"
    ;;

  *)
    echo "Usage: ./scripts/build.sh preview|final [--dry-run]"
    exit 1
    ;;
esac
