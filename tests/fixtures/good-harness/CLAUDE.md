# Example project

Node/TypeScript API. See `.claude/harness-spec.md` for the full harness inventory.
See @README.md for the public overview.

Maintainer: ops@acme.com — ping before changing the migration policy.

## Build & test
- `npm run dev` starts the server on port 3001.
- Run a single test file with `npm test -- path/to/file.test.ts`.
- Stay on react@18.2.0 until the router migration lands.

## IMPORTANT
Never write raw SQL in route handlers — use the query builder in `src/db/`.
A PreToolUse hook blocks commits containing raw SQL strings.

Writing `@README.md` in backticks keeps it literal, and the fenced block below
is likewise not parsed as an import:

```markdown
@docs/nope.md
```
