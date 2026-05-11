const BASE = 'http://localhost:8000'

export async function streamChat(question, chartContext) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, chart_context: chartContext }),
  })
  if (!res.ok) throw new Error(`streamChat failed: ${res.status}`)
  return res.body
}
