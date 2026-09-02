#!/bin/bash
# A Stop gate that can block but never reads stop_hook_active: with a suite
# that stays red it blocks every stop until Claude Code's own cap ends the turn.
cat >/dev/null
if npm test >/dev/null 2>&1; then exit 0; fi
echo '{"decision": "block", "reason": "npm test is failing"}'
exit 0
