#!/bin/bash
# A Stop gate with no loop guard: with a suite that stays red it blocks every
# stop until Claude Code's own cap ends the turn.
cat >/dev/null
if npm test >/dev/null 2>&1; then exit 0; fi
echo '{"decision": "block", "reason": "npm test is failing"}'
exit 0
