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

# Verify race-ready state
echo "Verifying race-ready state..."
ERRORS=0

# A/ should have friction files (committed)
for f in tags_v2.py TAGS_MIGRATION_PLAN.md; do
    if [[ ! -f "$SCRIPT_DIR/A/$f" ]]; then
        echo "  ERROR: A/$f missing (commit Phase 1 changes first)"
        ERRORS=$((ERRORS + 1))
    fi
done

# B/ tags/routes.py should have TODO, not a working POST endpoint
if grep -q "def add_tag" "$SCRIPT_DIR/B/tags/routes.py" 2>/dev/null; then
    echo "  ERROR: B/tags/routes.py still has add_tag implemented (commit Phase 2 changes first)"
    ERRORS=$((ERRORS + 1))
fi

if [[ $ERRORS -gt 0 ]]; then
    echo ""
    echo "WARNING: $ERRORS verification issue(s). Commit workshop changes before racing."
else
    echo "  A/ has 6+ conflicting tag concepts (friction files present)"
    echo "  B/ tags POST endpoint removed (TODO comment in place)"
    echo ""
    echo "Ready for race. Run: ./race.sh"
fi
