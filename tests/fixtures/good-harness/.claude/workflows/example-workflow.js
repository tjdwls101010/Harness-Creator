export const meta = {
  name: 'example-workflow',
  description: 'Fan out to find issues, verify each one, and report.',
  phases: [{ title: 'Find' }, { title: 'Verify' }],
}

phase('Find')
const found = await agent('List anything suspicious in src/.', {
  schema: { type: 'object', properties: { items: { type: 'array' } } },
})

const verified = await parallel(
  (found.items || []).map(item => () =>
    agent(`Verify this is a real issue: ${item}`, { phase: 'Verify' })
  )
)

log(`done: ${verified.filter(Boolean).length} verified`)
