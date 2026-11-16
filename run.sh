#!/usr/bin/env bash
# One command from a fresh clone: set up, rebuild veloxa.db from the raw packs, then
#   ./run.sh        run the cockpit
#   ./run.sh test   run the test set
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q --disable-pip-version-check -r requirements.txt
.venv/bin/python -m cockpit.load
case "${1:-run}" in
  test) .venv/bin/python -m unittest discover tests -v ;;
  run)  echo "Data model built. The cockpit UI arrives on Day 2 (see README)." ;;
  *)    echo "usage: ./run.sh [run|test]"; exit 2 ;;
esac
