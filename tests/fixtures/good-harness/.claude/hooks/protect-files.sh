#!/bin/bash
input=$(cat)
file=$(echo "$input" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)
case "$file" in
  *.env|*package-lock.json) echo "protected file" >&2; exit 2 ;;
  *) exit 0 ;;
esac
