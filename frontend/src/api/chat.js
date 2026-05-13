import { API_BASE as BASE } from './config.js'

export async function streamChat(question, chartContext, history = []) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, chart_context: chartContext, history }),
  })
  if (!res.ok) throw new Error(`streamChat failed: ${res.status}`)
  return res.body
}
