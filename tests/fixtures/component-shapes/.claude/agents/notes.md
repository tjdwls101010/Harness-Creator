---
name: notes
description: Read-only analyst that remembers what it learned. Use for repeated read-only investigations.
tools: Read, Grep, Glob
memory: project
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: ./guard.sh
          once: true
---

You read; you never modify.
