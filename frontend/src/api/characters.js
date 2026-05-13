import { API_BASE as BASE } from './config.js'

export async function fetchMentions() {
  const res = await fetch(`${BASE}/api/characters/mentions`)
  if (!res.ok) throw new Error(`fetchMentions failed: ${res.status}`)
  return res.json()
}

export async function fetchRelationships() {
  const res = await fetch(`${BASE}/api/characters/relationships`)
  if (!res.ok) throw new Error(`fetchRelationships failed: ${res.status}`)
  return res.json()
}
