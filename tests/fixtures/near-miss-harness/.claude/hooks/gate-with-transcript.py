#!/usr/bin/env python3
"""A one-shot Stop gate that guards by reading the transcript instead of the field."""
import json, sys
data = json.load(sys.stdin)
already = "gate-ran" in open(data["transcript_path"]).read() if data.get("transcript_path") else True
if already:
    sys.exit(0)
print(json.dumps({"decision": "block", "reason": "gate-ran: run the suite once"}))
