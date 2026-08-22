#!/bin/bash
# Recipe 3: a Stop-time validation gate. Fires once per turn, including the
# turns that changed nothing -- that cost is accepted here deliberately
# because this project's suite is fast.
input=$(cat)
active=$(echo "$input" | python3 -c "import json,sys; print(json.load(sys.stdin).get('stop_hook_active', False))" 2>/dev/null)
# Loop guard, first and unconditional: a suite that stays red would
# otherwise block every stop until Claude Code's own cap ends the turn.
if [ "$active" = "True" ]; then exit 0; fi

if output=$(npm test 2>&1); then exit 0; fi

# Decision channel, not the exit-2 channel: Stop reads the top-level
# `decision` field, and stdout JSON is parsed only when the hook exits 0.
FAILURE="$output" python3 -c "
import json, os
tail = os.environ['FAILURE'].splitlines()[-20:]
print(json.dumps({'decision': 'block',
                  'reason': 'npm test is failing:\n' + '\n'.join(tail)}))
"
exit 0
