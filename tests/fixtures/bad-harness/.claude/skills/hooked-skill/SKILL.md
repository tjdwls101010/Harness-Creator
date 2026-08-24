---
name: hooked-skill
description: A skill whose frontmatter hooks block is wrong in two ways, for the linter to find. Use when testing validate_harness.py against skill-scoped hooks.
hooks:
  NotARealEvent:
    - hooks:
        - type: command
          command: hooks/absent.sh
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: hooks/absent.sh
        - type: command
          command: ${CLAUDE_PROJECT_DIR}/.claude/hooks/noop.sh
---

# hooked-skill

Fixture only.
