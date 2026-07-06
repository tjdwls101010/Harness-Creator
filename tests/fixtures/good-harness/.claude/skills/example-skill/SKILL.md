---
name: example-skill
description: >
  Handles the example domain task for this fixture project. Use whenever the
  user asks to run the example task or mentions the example workflow.
---

# Example skill

See `references/detail.md` for the full procedure and `scripts/run.py` for the CLI.

The one gotcha that matters: the example API is idempotent only on retry, not on first call.
