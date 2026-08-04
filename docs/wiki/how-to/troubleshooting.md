# Troubleshoot Harness Creator

Use this guide to resolve common installation, invocation, validation, and re-entry problems.

## 1. The skill does not appear

Check the active installation path:

```bash
claude plugin list
npx skills list --agent claude-code
```

For a plugin install, refresh the marketplace, update the plugin, and run `/reload-plugins` or start a fresh session. For a symlink, confirm `readlink ~/.claude/skills/harness-creator` points to an existing checkout.

## 2. The skill appears twice

You have more than one install path active. The plugin is namespaced while skills CLI and symlink installs are bare. Choose one path, uninstall the others with the commands in [Install and update](install-and-update.md), then restart Claude Code.

## 3. The marketplace cannot be added

Confirm the repository is reachable and contains `.claude-plugin/marketplace.json` on its default branch. Use the exact owner/repository spelling:

```bash
claude plugin marketplace add tjdwls101010/Harness-Creator
```

If organizational policy restricts marketplaces, ask the administrator to allow this source. Do not work around a managed restriction.

## 4. An update is not visible

Refresh and reload:

```bash
claude plugin marketplace update harness-creator
claude plugin update harness-creator@harness-creator
```

Then run `/reload-plugins` or start a new session. Local plugin installs use a cache; editing the source checkout does not update that cached copy. Contributors should prefer the development symlink and keep the plugin uninstalled during editing.

## 5. Validation reports drift

Run the audit for the full list:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/audit_harness.py --path .
```

Do not delete unexpected files automatically. Follow [Synchronize drift](sync-drift.md) and decide whether the spec or disk is authoritative for each item.

## 6. A hook test does not block

Confirm the event supports blocking, the matcher selects the input, the handler is executable, and the exit/output contract is correct. Exit `1` normally signals a non-blocking hook error; for most blocking events, exit `2` plus standard error carries the denial reason.

Use `test_hook.py --matrix` before executing the handler.

## 7. The interview asks about known repository facts

Point the skill to the manifest, configuration, or command that already answers the question. The interview should state discovered facts and ask only for unresolved intent. If the repository contains conflicting sources, explain which one is authoritative.

## 8. The E2E run is inconclusive

Do not convert runner uncertainty into a product claim. Save the transcript, note the permission mode and Claude Code version, and reduce the next scenario to a read-only observation. See [Run E2E validation](run-e2e-validation.md) for the runner boundary.

## 9. Get help

Use [SUPPORT.md](../../../SUPPORT.md) to choose between FAQ, a bug report, a feature request, a documentation issue, or private security reporting. Support is best effort and has no response-time guarantee.

## 10. Next

Read the [FAQ](../reference/faq.md) for conceptual questions or the [CLI reference](../reference/cli.md) for exact options. Return to the [documentation index](../README.md).
