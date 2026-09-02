const NAME = 'nightly'
export const meta = { name: NAME }

import fs from 'node:fs'
import { execSync } from 'node:child_process'

const files = fs.readdirSync('src')
execSync('npm test')
const r = await agent(`Summarize ${files.length} files using ${CLAUDE_SKILL_DIR}/scripts/tool.py`)
return { r }
