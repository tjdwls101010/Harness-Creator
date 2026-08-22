# Example project

Node/TypeScript API. See @README.md for the public overview.

Maintainer: ops@acme.com — ping before changing the migration policy.

## Build & test
- `npm run dev` starts the server on port 3001.
- Run a single test file with `npm test -- path/to/file.test.ts`.
- Stay on react@18.2.0 until the router migration lands.

## IMPORTANT
Never write raw SQL in route handlers — use the query builder in `src/db/`.
`.claude/hooks/protect-files.sh` blocks writes to `.env` and `package-lock.json`, including writes made through `Bash`.
`.claude/hooks/check-tests.sh` holds the turn open until `npm test` passes.

Writing `@README.md` in backticks keeps it literal, and the fenced block below
is likewise not parsed as an import:

```markdown
@docs/nope.md
```
