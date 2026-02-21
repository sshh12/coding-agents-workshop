#!/bin/bash
# Auto-lint Python files after edits
FILE_PATH=$(cat /dev/stdin | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)
if [[ "$FILE_PATH" == *.py ]]; then
    ruff check --fix "$FILE_PATH" 2>/dev/null
fi
exit 0
