import { useState, useEffect } from 'react'
import { fetchSentiment, fetchWordCount } from '../../api/story'
import { fetchMentions, fetchRelationships } from '../../api/characters'
import Card from '../Card'

const BOOK_TITLES = {
  1: "Philosopher's Stone",
  2: "Chamber of Secrets",
  3: "Prisoner of Azkaban",
  4: "Goblet of Fire",
  5: "Order of the Phoenix",
  6: "Half-Blood Prince",
  7: "Deathly Hallows",
}

function KpiCard({ label, value, sub, loading, error }) {
  return (
    <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-lg p-5 flex flex-col gap-2 min-h-[100px]">
      <span className="text-xs font-medium text-warm-400 uppercase tracking-wider">{label}</span>
      {loading && <div className="h-7 w-32 bg-neutral-700 rounded animate-pulse mt-1" />}
      {!loading && error && <span className="text-sm text-red-500/70">Failed to load</span>}
      {!loading && !error && (
        <>
          <span className="text-lg font-semibold text-warm-100 leading-snug">{value}</span>
          {sub && <span className="text-xs text-warm-400">{sub}</span>}
        </>
      )}
    </div>
  )
}

export default function OverviewPage() {
  const [wc, setWc]     = useState({ data: null, loading: true, error: false })
  const [sent, setSent] = useState({ data: null, loading: true, error: false })
  const [men, setMen]   = useState({ data: null, loading: true, error: false })
  const [rel, setRel]   = useState({ data: null, loading: true, error: false })

  useEffect(() => {
    fetchWordCount()
      .then(d => setWc({ data: d, loading: false, error: false }))
      .catch(() => setWc({ data: null, loading: false, error: true }))
    fetchSentiment()
      .then(d => setSent({ data: d, loading: false, error: false }))
      .catch(() => setSent({ data: null, loading: false, error: true }))
    fetchMentions()
      .then(d => setMen({ data: d, loading: false, error: false }))
      .catch(() => setMen({ data: null, loading: false, error: true }))
    fetchRelationships()
      .then(d => setRel({ data: d, loading: false, error: false }))
      .catch(() => setRel({ data: null, loading: false, error: true }))
  }, [])

  // Word-count derived KPIs
  const totalChapters = wc.data ? String(wc.data.length) : null
  const totalWords = wc.data
    ? wc.data.reduce((s, c) => s + c.word_count, 0).toLocaleString()
    : null
  let longestBookValue = null, longestBookSub = null
  if (wc.data) {
    const byBook = {}
    wc.data.forEach(c => { byBook[c.book] = (byBook[c.book] || 0) + c.word_count })
    const [bookNum, words] = Object.entries(byBook).sort((a, b) => b[1] - a[1])[0]
    longestBookValue = BOOK_TITLES[+bookNum]
    longestBookSub = `${words.toLocaleString()} words`
  }

  // Mentions derived KPI
  let topCharValue = null, topCharSub = null
  if (men.data) {
    const totals = {}
    men.data.forEach(r => { totals[r.character] = (totals[r.character] || 0) + r.mention_count })
    const [name, count] = Object.entries(totals).sort((a, b) => b[1] - a[1])[0]
    topCharValue = name
    topCharSub = `${count.toLocaleString()} total mentions`
  }

  // Sentiment derived KPIs
  let posValue = null, posSub = null, negValue = null, negSub = null
  if (sent.data) {
    const sorted = [...sent.data].sort((a, b) => b.compound - a.compound)
    const pos = sorted[0]
    posValue = `${BOOK_TITLES[pos.book]}, Ch. ${pos.chapter}`
    posSub = `compound ${pos.compound.toFixed(4)}`
    const neg = sorted[sorted.length - 1]
    negValue = `${BOOK_TITLES[neg.book]}, Ch. ${neg.chapter}`
    negSub = `compound ${neg.compound.toFixed(4)}`
  }

  // Relationships derived KPI
  let connValue = null, connSub = null
  if (rel.data?.nodes) {
    const top = [...rel.data.nodes].sort((a, b) => b.pagerank - a.pagerank)[0]
    connValue = top.id
    connSub = `PageRank ${top.pagerank.toFixed(4)} · degree ${top.degree}`
  }

  return (
    <section className="p-6 space-y-4">
      <h2 className="text-lg font-semibold text-warm-100 tracking-tight">Overview</h2>
      <Card title="Series at a Glance">
        <div className="grid grid-cols-2 xl:grid-cols-3 gap-4">
          <KpiCard label="Total Chapters"         value={totalChapters}   loading={wc.loading}   error={wc.error} />
          <KpiCard label="Total Words"            value={totalWords}       loading={wc.loading}   error={wc.error} />
          <KpiCard label="Longest Book"           value={longestBookValue} sub={longestBookSub}   loading={wc.loading}   error={wc.error} />
          <KpiCard label="Top Character"          value={topCharValue}     sub={topCharSub}        loading={men.loading}  error={men.error} />
          <KpiCard label="Most Positive Chapter"  value={posValue}         sub={posSub}            loading={sent.loading} error={sent.error} />
          <KpiCard label="Most Negative Chapter"  value={negValue}         sub={negSub}            loading={sent.loading} error={sent.error} />
          <KpiCard label="Most Connected"         value={connValue}        sub={connSub}           loading={rel.loading}  error={rel.error} />
        </div>
      </Card>
    </section>
  )
}
