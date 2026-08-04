# Install and update Harness Creator

Use this guide to choose one installation method, update it deliberately, and avoid duplicate skill registration.

## 1. Choose one path

| Path | Use it when | Invocation |
|---|---|---|
| Claude Code plugin | You want the recommended distribution experience | `/harness-creator:harness-creator` |
| skills CLI | You want the skill without the repository marketplace | `/harness-creator` |
| Development symlink | You are editing this checkout | `/harness-creator` |

Do not activate more than one path at a time.

## 2. Install the Claude Code plugin

```bash
claude plugin marketplace add tjdwls101010/Harness-Creator
claude plugin install harness-creator@harness-creator
```

Start a fresh session or run `/reload-plugins` before invoking the skill.

Update the marketplace and plugin when a new release is available:

```bash
claude plugin marketplace update harness-creator
claude plugin update harness-creator@harness-creator
```

Remove the plugin before switching install paths:

```bash
claude plugin uninstall harness-creator@harness-creator
```

Use `claude plugin marketplace remove harness-creator` only when you also want to remove the repository marketplace.

## 3. Install with the skills CLI

```bash
npx skills add tjdwls101010/Harness-Creator --agent claude-code --skill harness-creator
```

List the installed skill:

```bash
npx skills list --agent claude-code
```

Update it from its recorded source:

```bash
npx skills update harness-creator
```

Remove it before switching paths:

```bash
npx skills remove harness-creator --agent claude-code
```

## 4. Create a development symlink

From this repository:

```bash
ln -s "$(pwd)/.claude/skills/harness-creator" ~/.claude/skills/harness-creator
```

Confirm the link target before deleting it later:

```bash
readlink ~/.claude/skills/harness-creator
```

Remove only that symlink when you finish development. Do not recursively delete the source directory.

## 5. Verify the active path

Open a fresh Claude Code session and check the invocation name. The plugin path is namespaced; the skills CLI and symlink paths are bare. If both names appear, uninstall one path and restart.

## 6. Next

Continue with [Create your first harness](../tutorials/first-harness.md), or use [Troubleshooting](troubleshooting.md) if the skill does not appear. Return to the [documentation index](../README.md).
