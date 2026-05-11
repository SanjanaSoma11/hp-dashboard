const BASE = 'http://localhost:8000'

export async function fetchMentions() {
  const res = await fetch(`${BASE}/api/characters/mentions`)
  if (!res.ok) throw new Error(`fetchMentions failed: ${res.status}`)
  return res.json()
}
