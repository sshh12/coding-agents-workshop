#!/usr/bin/env bash
# race.sh - Run both agents in parallel and capture timing + output
# Usage: ./race.sh [--prompt "custom prompt"]
#
# Prerequisites:
#   - claude CLI installed and authenticated
#   - Both A/ and B/ repos set up with dependencies installed
#   - Both repos in clean git state

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_A="$SCRIPT_DIR/A"
REPO_B="$SCRIPT_DIR/B"
RESULTS_DIR="$SCRIPT_DIR/race-results/$(date +%Y%m%d-%H%M%S)"

# Default prompt
PROMPT='Add a new feature: experiment tagging. Users should be able to add tags to experiments via a new API endpoint POST /api/experiments/{id}/tags (accepting a JSON body with a "name" field) and see tags displayed on the experiment detail page. Follow the existing patterns in the codebase. Run the tests to verify your changes work.'

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

ALLOWED_TOOLS="Bash,Read,Write,Edit,Glob,Grep"

mkdir -p "$RESULTS_DIR"

echo "============================================"
echo "  AGENT RACE"
echo "============================================"
echo ""
echo "Prompt: $PROMPT"
echo "Results: $RESULTS_DIR"
echo ""

# Save the prompt
echo "$PROMPT" > "$RESULTS_DIR/prompt.txt"

# Function to run an agent and capture output
run_agent() {
    local label="$1"
    local workdir="$2"
    local output_file="$RESULTS_DIR/${label}.jsonl"
    local log_file="$RESULTS_DIR/${label}.log"
    local time_file="$RESULTS_DIR/${label}.time"

    echo "[$label] Starting agent in $workdir..."

    # Record start time
    local start_time=$(date +%s)

    # Run claude with stream-json output, capture everything
    # Unset CLAUDECODE to allow nested sessions
    cd "$workdir"
    env -u CLAUDECODE claude -p "$PROMPT" \
        --output-format stream-json \
        --verbose \
        --allowedTools "$ALLOWED_TOOLS" \
        > "$output_file" 2>"$log_file" || true

    # Record end time
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))

    echo "$elapsed" > "$time_file"
    echo "[$label] Finished in ${elapsed}s"
}

# Run both agents in parallel
echo "Starting both agents..."
echo ""

run_agent "A-before" "$REPO_A" &
PID_A=$!

run_agent "B-after" "$REPO_B" &
PID_B=$!

# Wait for both to finish
echo "Waiting for agents to complete..."
echo "(Press Ctrl+C to abort both)"
echo ""

wait $PID_A 2>/dev/null || true
wait $PID_B 2>/dev/null || true

echo ""
echo "============================================"
echo "  RESULTS"
echo "============================================"
echo ""

# Read timing
TIME_A=$(cat "$RESULTS_DIR/A-before.time" 2>/dev/null || echo "DNF")
TIME_B=$(cat "$RESULTS_DIR/B-after.time" 2>/dev/null || echo "DNF")

echo "Version A (Before): ${TIME_A}s"
echo "Version B (After):  ${TIME_B}s"
echo ""

# Count tool calls from stream-json output
count_tool_calls() {
    local file="$1"
    if [[ -f "$file" ]]; then
        grep -c '"type":"tool_use"' "$file" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

TOOLS_A=$(count_tool_calls "$RESULTS_DIR/A-before.jsonl")
TOOLS_B=$(count_tool_calls "$RESULTS_DIR/B-after.jsonl")

echo "Tool calls (A): $TOOLS_A"
echo "Tool calls (B): $TOOLS_B"
echo ""

# Check if tests pass in B
echo "Verifying Version B tests..."
cd "$REPO_B"
if pytest --tb=short -q 2>/dev/null; then
    echo "Version B: ALL TESTS PASS"
else
    echo "Version B: SOME TESTS FAILED"
fi

echo ""
echo "Full output saved to: $RESULTS_DIR/"
echo "  A-before.jsonl  - Agent A stream output"
echo "  B-after.jsonl   - Agent B stream output"
echo "  A-before.log    - Agent A stderr/verbose log"
echo "  B-after.log     - Agent B stderr/verbose log"
echo "  prompt.txt      - The prompt used"
