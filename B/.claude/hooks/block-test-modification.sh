#!/bin/bash
# Block any edits to the tests/ directory
INPUT=$(cat /dev/stdin)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)
if [[ "$FILE_PATH" == tests/* ]]; then
    echo '{"decision": "block", "reason": "Test files are protected. Do not modify tests/."}'
    exit 2
fi
exit 0
