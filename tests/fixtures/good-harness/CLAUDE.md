# Example project

Node/TypeScript API. See `.claude/harness-spec.md` for the full harness inventory.

## Build & test
- `npm run dev` starts the server on port 3001.
- Run a single test file with `npm test -- path/to/file.test.ts`.

## IMPORTANT
Never write raw SQL in route handlers — use the query builder in `src/db/`.
A PreToolUse hook blocks commits containing raw SQL strings.
