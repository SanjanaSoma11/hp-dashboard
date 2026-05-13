import { API_BASE as BASE } from './config.js'

export async function fetchSentiment() {
  const res = await fetch(`${BASE}/api/story/sentiment`)
  if (!res.ok) throw new Error(`fetchSentiment failed: ${res.status}`)
  return res.json()
}

export async function fetchWordCount() {
  const res = await fetch(`${BASE}/api/story/wordcount`)
  if (!res.ok) throw new Error(`fetchWordCount failed: ${res.status}`)
  return res.json()
}

export async function fetchDeaths() {
  const res = await fetch(`${BASE}/api/story/deaths`)
  if (!res.ok) throw new Error(`fetchDeaths failed: ${res.status}`)
  return res.json()
}
