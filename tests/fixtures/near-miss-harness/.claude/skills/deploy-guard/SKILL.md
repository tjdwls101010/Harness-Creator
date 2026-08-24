---
name: deploy-guard
description: Guard the deploy script against being pointed at production by accident. Use when the user asks to deploy, ship, or release, and when a deploy command is being drafted. Not for local builds or test runs, which no guard covers.
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: hooks/check-target.sh
        - type: command
          command: hooks/check-target.sh
          once: true
---

# deploy-guard

The deploy script takes `--env` and refuses to run without it, so the ordinary
mistake is impossible. What remains is the one this hook covers: a `--env prod`
typed during a session that was only ever meant to touch staging.
