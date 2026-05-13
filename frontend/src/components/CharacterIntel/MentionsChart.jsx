import { useState, useEffect, useMemo } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { fetchMentions } from '../../api/characters'
import { useFilter } from '../../context/FilterContext'
import CharacterFilter from './CharacterFilter'
import { COLORS } from '../../utils/colors'
import { THEME, BOOK_TITLES } from '../../utils/theme'

function buildChartData(records) {
  const pairMap = new Map()
  records.forEach(r => {
    const key = `${r.book}:${r.chapter}`
    if (!pairMap.has(key)) pairMap.set(key, { book: r.book, chapter: r.chapter })
  })
  const pairs = [...pairMap.values()].sort((a, b) => a.book - b.book || a.chapter - b.chapter)
  const rowIdx = new Map(pairs.map((p, i) => [`${p.book}:${p.chapter}`, i]))
  const rows = pairs.map((p, i) => ({ index: i, book: p.book, chapter: p.chapter }))
  records.forEach(r => {
    const i = rowIdx.get(`${r.book}:${r.chapter}`)
    if (i !== undefined) rows[i][r.character] = r.mention_count
  })
  return rows
}

function topByTotal(records, n) {
  const totals = {}
  records.forEach(r => { totals[r.character] = (totals[r.character] || 0) + r.mention_count })
  return Object.entries(totals)
    .sort(([, a], [, b]) => b - a)
    .slice(0, n)
    .map(([name], i) => ({ name, color: COLORS[i % COLORS.length] }))
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  const bookTitle = BOOK_TITLES[d?.book] || `Book ${d?.book}`
  return (
    <div className="bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-xs text-neutral-200 max-w-[200px]">
      <p className="font-medium text-neutral-100 truncate">{bookTitle}</p>
      <p className="text-neutral-400 mb-1">Chapter {d?.chapter}</p>
      {payload.map(p => (
        <p key={p.dataKey} style={{ color: p.color }}>{p.name}: {p.value}</p>
      ))}
    </div>
  )
}

export default function MentionsChart({ onContextChange }) {
  const { selectedBooks } = useFilter()
  const [allRecords, setAllRecords] = useState([])
  const [selected, setSelected] = useState(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchMentions()
      .then(data => {
        setAllRecords(data)
        const t20 = topByTotal(data, 20)
        setSelected(new Set(t20.slice(0, 10).map(c => c.name)))
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const filteredRecords = useMemo(
    () => allRecords.filter(r => selectedBooks.includes(r.book)),
    [allRecords, selectedBooks]
  )

  const top20 = useMemo(() => topByTotal(filteredRecords, 20), [filteredRecords])
  const chartData = useMemo(() => buildChartData(filteredRecords), [filteredRecords])
  const activeChars = top20.filter(c => selected.has(c.name))

  useEffect(() => {
    if (!top20.length) return
    onContextChange?.({
      chart: 'mentions',
      activeCharacters: [...selected],
      topCharacter: top20[0]?.name,
    })
  }, [selected, top20, onContextChange])

  function toggleChar(name) {
    setSelected(prev => {
      const next = new Set(prev)
      next.has(name) ? next.delete(name) : next.add(name)
      return next
    })
  }

  if (loading) return <div className="flex items-center justify-center h-64 text-neutral-500 text-sm">Loading mentions…</div>
  if (error) return <div className="flex items-center justify-center h-64 text-red-400 text-sm">Error: {error}</div>
  if (!selectedBooks.length || !filteredRecords.length) return <div className="flex items-center justify-center h-32 text-neutral-500 text-sm">No books selected</div>

  return (
    <div>
      <CharacterFilter characters={top20} selected={selected} onToggle={toggleChar} />
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 8, right: 16, bottom: 24, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={THEME.chart.grid} />
          <XAxis
            dataKey="index"
            tick={{ fill: THEME.chart.tick, fontSize: 11 }}
            label={{ value: 'Chapter (series)', position: 'insideBottom', offset: -12, fill: THEME.chart.label, fontSize: 11 }}
          />
          <YAxis
            tick={{ fill: THEME.chart.tick, fontSize: 11 }}
            label={{ value: 'Mentions', angle: -90, position: 'insideLeft', offset: 12, fill: THEME.chart.label, fontSize: 11 }}
          />
          <Tooltip content={<CustomTooltip />} />
          {activeChars.map(({ name, color }) => (
            <Line key={name} type="monotone" dataKey={name} name={name} stroke={color} dot={false} strokeWidth={1.5} connectNulls />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
