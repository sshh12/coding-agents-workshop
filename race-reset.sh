#!/usr/bin/env bash
# race-reset.sh - Reset both repos to clean state before a race
# Usage: ./race-reset.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Resetting Version A..."
cd "$SCRIPT_DIR/A"
git checkout -- .
git clean -fd

echo "Resetting Version B..."
cd "$SCRIPT_DIR/B"
git checkout -- .
git clean -fd

echo "Both repos reset to clean state."
echo ""
echo "Ready for race. Run: ./race.sh"
