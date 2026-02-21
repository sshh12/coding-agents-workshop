#!/usr/bin/env bash
# race-analyze.sh - Analyze the most recent race results
# Usage: ./race-analyze.sh [results-dir]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find the most recent results directory, or use the one provided
if [[ $# -gt 0 ]]; then
    RESULTS_DIR="$1"
else
    RESULTS_DIR=$(ls -dt "$SCRIPT_DIR"/race-results/*/ 2>/dev/null | head -1)
    if [[ -z "$RESULTS_DIR" ]]; then
        echo "No race results found. Run race.sh first."
        exit 1
    fi
fi

echo "Analyzing: $RESULTS_DIR"
echo ""

# Parse stream-json for tool usage breakdown
analyze_tools() {
    local file="$1"
    local label="$2"

    if [[ ! -f "$file" ]]; then
        echo "  [$label] No output file found"
        return
    fi

    echo "  [$label] Tool usage breakdown:"

    # Count each tool type
    for tool in Read Write Edit Glob Grep Bash; do
        local count=$(grep -o "\"name\":\"$tool\"" "$file" 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$count" -gt 0 ]]; then
            echo "    $tool: $count"
        fi
    done

    # Count total tokens if available
    local input_tokens=$(grep -o '"input_tokens":[0-9]*' "$file" 2>/dev/null | tail -1 | grep -o '[0-9]*' || echo "N/A")
    local output_tokens=$(grep -o '"output_tokens":[0-9]*' "$file" 2>/dev/null | tail -1 | grep -o '[0-9]*' || echo "N/A")
    echo "    Input tokens: $input_tokens"
    echo "    Output tokens: $output_tokens"
    echo ""
}

echo "--- Timing ---"
echo "  Version A: $(cat "$RESULTS_DIR/A-before.time" 2>/dev/null || echo 'N/A')s"
echo "  Version B: $(cat "$RESULTS_DIR/B-after.time" 2>/dev/null || echo 'N/A')s"
echo ""

echo "--- Tool Usage ---"
analyze_tools "$RESULTS_DIR/A-before.jsonl" "Version A"
analyze_tools "$RESULTS_DIR/B-after.jsonl" "Version B"

echo "--- Files Modified ---"
echo "  Version A:"
cd "$SCRIPT_DIR/A"
git diff --name-only -- . 2>/dev/null | sed 's/^/    /' || echo "    (no changes or not a git repo)"
echo ""
echo "  Version B:"
cd "$SCRIPT_DIR/B"
git diff --name-only -- . 2>/dev/null | sed 's/^/    /' || echo "    (no changes or not a git repo)"
echo ""

echo "--- Test Results ---"
echo "  Version B:"
cd "$SCRIPT_DIR/B"
PYTEST=$(.venv/bin/pytest --version >/dev/null 2>&1 && echo ".venv/bin/pytest" || echo "pytest")
$PYTEST --tb=line -q 2>&1 | tail -5 | sed 's/^/    /'
echo ""

echo "Done. Full logs in $RESULTS_DIR/"
