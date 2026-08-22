#!/bin/bash
# Matched on Edit|Write|Bash. The Bash arm is not optional: `sed -i` and
# `echo >> file` reach a protected path without ever calling Edit or Write,
# so an Edit|Write-only matcher never sees them.
input=$(cat)
read -r tool <<<"$(echo "$input" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)"

if [ "$tool" = "Bash" ]; then
  # The target is buried in a command string, so this is a substring scan,
  # not a path match -- deliberately broad, and paired with the deny rules
  # in settings.json because a scan over shell text is not a parser.
  command=$(echo "$input" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)
  case "$command" in
    *.env*|*package-lock.json*) echo "protected file named in command" >&2; exit 2 ;;
  esac
  exit 0
fi

file=$(echo "$input" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)
case "$file" in
  *.env|*package-lock.json) echo "protected file" >&2; exit 2 ;;
  *) exit 0 ;;
esac
