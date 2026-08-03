export const meta = {
  name: 'v3-compression-pilot',
  description: 'Pilot the v3 compression discriminant and claim-preservation A/B on agents.md',
  phases: [
    { title: 'Extract-original', detail: 'two independent claim extractions from the untouched file' },
    { title: 'Compress', detail: 'two independent compressions using the draft discriminant' },
    { title: 'Extract-compressed', detail: 'blind re-extraction from each compressed version' },
    { title: 'Judge', detail: 'diff claim sets, report losses and dilution' },
  ],
}

const SRC = '/Users/seongjin/Coding/harness-creator/.claude/skills/harness-creator/references/agents.md'
const OUT = '/private/tmp/claude-501/-Users-seongjin-Coding-harness-creator/d218c4f0-7fb2-41ae-90ef-22497d389d5d/scratchpad'

const CLAIM_SCHEMA = {
  type: 'object',
  properties: {
    claims: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'short kebab slug naming the claim' },
          claim: { type: 'string', description: 'the atomic falsifiable statement, one sentence' },
          kind: { type: 'string', enum: ['mechanism', 'decision-rule', 'test', 'counter-case', 'silent-failure', 'number-with-exception', 'rationale'] },
        },
        required: ['id', 'claim', 'kind'],
      },
    },
  },
  required: ['claims'],
}

const EXTRACT_RULES = `
Extract every ATOMIC CLAIM. An atomic claim is one falsifiable statement that, if it vanished, would leave a reader of this file unable to get something right.

Classify each by kind:
- mechanism: a factual statement about how Claude Code behaves (a field name, a default, a version floor, an exact value, what loads when)
- decision-rule: a statement telling the reader what to choose and under which condition
- test: a question or check the reader is told to apply ("ask whether X", "the check is Y")
- counter-case: an example of where a rule does NOT apply
- silent-failure: a statement that some failure produces no error / no warning / no signal
- number-with-exception: a threshold plus the case where it does not hold
- rationale: a stated reason for a rule

Be exhaustive and granular. A 200-word paragraph typically holds 3-8 atomic claims. Do NOT merge two claims into one entry. Do NOT include pure connective prose, restatements, or motivational sentences as claims.
`

const DISCRIMINANT = `
You are compressing a reference file that Claude reads while generating a Claude Code harness. The reader is Claude, not a skeptical human. Conviction is a property of CONTENT (the why is present), not of VOLUME (the why is argued at length).

Apply these techniques, in this order of preference:

T1 - TABULATE. Any passage that enumerates N options, each carrying a when/why/cost, becomes a markdown table. Every fact keeps its own cell; only the connective prose between them is deleted. This is the highest-yield, lowest-risk move: no claim can be lost by construction.

T2 - DELETE SCAFFOLDING. Delete sentences whose removal changes no claim:
  * Restatement - the same claim said again in different words (a thesis, then a "the test is the same either way" recap of that thesis)
  * Persuasion - sentences aimed at making a skeptical human agree ("Resist that.", "This is not stylistic softness, it's mechanical:", "The temptation in a meta-skill like this one is...")
  * Derivable elaboration - a consequence the model computes instantly from the premise already stated
  * Symmetric enumeration - the negative case spelled out at full length when the positive case already implies it
  * Meta-narration - "The practical implication:", "Concretely, when...", "Three things in that body are the transferable part"

T3 - MERGE RESTATEMENTS. One claim, one sentence, in its strongest phrasing.

FORBIDDEN TECHNIQUE: paraphrase-shorter. Do NOT rewrite a paragraph into a shorter paragraph of your own words. That is where meaning silently dilutes. You may only tabulate, delete whole sentences/clauses, and merge duplicate statements. Surviving sentences should be recognizably the original sentences.

NEVER CUT (these look like padding and are not):
  * The TEST SENTENCE - any sentence that hands the reader a check to apply ("ask whether X", "would deleting this line cause Claude to be wrong?"). This is the operational half of a principle.
  * The NUMBER'S EXCEPTION - a threshold and the case where it does not apply travel together.
  * The COUNTER-CASE - the example showing where the rule does NOT apply. Without it the rule over-applies.
  * The SILENT-FAILURE CLAUSE - any "and nothing tells you" / "no error" / "silently" statement. That is the entire value of a gotcha.
  * Any NAMED PRODUCT MECHANISM - a field name, a version floor, an exact value, a file path, a tool name.
  * The WHY when it is non-obvious. Keep one clause of it. ("because auto memory is nondeterministic" stays; "because that would be slower" goes - derivable.)

Preserve the file's heading structure and all fenced code blocks verbatim unless a code block is itself pure duplication.
`

phase('Extract-original')
phase('Compress')

const round1 = await parallel([
  () => agent(`Read ${SRC} in full.\n${EXTRACT_RULES}\nReturn the claim list for the WHOLE file.`,
    { label: 'extract-orig-A', phase: 'Extract-original', schema: CLAIM_SCHEMA, model: 'sonnet' }),
  () => agent(`Read ${SRC} in full.\n${EXTRACT_RULES}\nReturn the claim list for the WHOLE file.`,
    { label: 'extract-orig-B', phase: 'Extract-original', schema: CLAIM_SCHEMA, model: 'sonnet' }),
  () => agent(`Read ${SRC} in full, then compress it.\n${DISCRIMINANT}\n\nWrite the compressed file to ${OUT}/agents-compressed-A.md. Then return ONLY a JSON object with keys: originalWords, compressedWords, techniquesUsed (array of strings), tablesCreated (number), and notes (a short string naming anything you were unsure whether to cut).`,
    { label: 'compress-A', phase: 'Compress', model: 'sonnet' }),
  () => agent(`Read ${SRC} in full, then compress it.\n${DISCRIMINANT}\n\nWrite the compressed file to ${OUT}/agents-compressed-B.md. Then return ONLY a JSON object with keys: originalWords, compressedWords, techniquesUsed (array of strings), tablesCreated (number), and notes (a short string naming anything you were unsure whether to cut).`,
    { label: 'compress-B', phase: 'Compress', model: 'sonnet' }),
])

log(`round 1 done: ${round1.filter(Boolean).length}/4 agents returned`)

phase('Extract-compressed')
const blind = await parallel([
  () => agent(`Read ${OUT}/agents-compressed-A.md in full. This is the ONLY file you may read; do not look for any other version of it.\n${EXTRACT_RULES}\nReturn the claim list for the WHOLE file.`,
    { label: 'extract-compressed-A', phase: 'Extract-compressed', schema: CLAIM_SCHEMA, model: 'sonnet' }),
  () => agent(`Read ${OUT}/agents-compressed-B.md in full. This is the ONLY file you may read; do not look for any other version of it.\n${EXTRACT_RULES}\nReturn the claim list for the WHOLE file.`,
    { label: 'extract-compressed-B', phase: 'Extract-compressed', schema: CLAIM_SCHEMA, model: 'sonnet' }),
])

const origClaims = [round1[0], round1[1]].filter(Boolean)
const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    lostClaims: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, claim: { type: 'string' }, kind: { type: 'string' }, severity: { type: 'string', enum: ['critical', 'moderate', 'minor'] } }, required: ['id', 'claim', 'kind', 'severity'] } },
    weakenedClaims: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, before: { type: 'string' }, after: { type: 'string' }, why: { type: 'string' } }, required: ['id', 'before', 'after', 'why'] } },
    survivedCount: { type: 'number' },
    originalCount: { type: 'number' },
    assessment: { type: 'string', description: 'two sentences: is this compression safe to ship, and what discriminant rule (if any) failed to prevent the losses' },
  },
  required: ['lostClaims', 'weakenedClaims', 'survivedCount', 'originalCount', 'assessment'],
}

phase('Judge')
const verdicts = await parallel(['A', 'B'].map((v, i) => () =>
  agent(`Two claim lists were extracted from a reference file: one from the ORIGINAL, one from a COMPRESSED version produced by an independent agent that was told to preserve every claim.

ORIGINAL CLAIMS (union of two independent extractions; treat near-duplicates across the two as one claim):
${JSON.stringify(origClaims)}

CLAIMS FOUND IN THE COMPRESSED VERSION:
${JSON.stringify(blind[i])}

You may read ${OUT}/agents-compressed-${v}.md and ${SRC} to adjudicate borderline cases.

For every original claim, decide: does it survive in the compressed version at full strength, survive but weakened (hedged, generalized, stripped of its condition or its exception), or is it gone? Report only the losses and the weakenings. Be strict: a claim that survives as a table cell at full fidelity SURVIVES; a claim whose "silently / no error" clause was dropped is WEAKENED even if the rest is intact.`,
    { label: `judge-${v}`, phase: 'Judge', schema: VERDICT_SCHEMA, model: 'sonnet' })))

return {
  compressionA: round1[2],
  compressionB: round1[3],
  origClaimCounts: origClaims.map(c => c && c.claims ? c.claims.length : 0),
  blindClaimCounts: blind.map(c => c && c.claims ? c.claims.length : 0),
  verdicts: verdicts.filter(Boolean),
}
