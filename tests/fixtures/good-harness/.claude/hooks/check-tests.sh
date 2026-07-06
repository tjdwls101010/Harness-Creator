#!/bin/bash
input=$(cat)
active=$(echo "$input" | python3 -c "import json,sys; print(json.load(sys.stdin).get('stop_hook_active', False))" 2>/dev/null)
if [ "$active" = "True" ]; then exit 0; fi
exit 0
