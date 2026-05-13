import { useState, useEffect, useMemo } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { fetchSentiment } from '../../api/story'
import { useFilter } from '../../context/FilterContext'
import { THEME } from '../../utils/theme'

const BOOK_COLORS = ['#818cf8', '#34d399', '#fb923c', '#f472b6', '#facc15', '#38bdf8', '#a78bfa']

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div className="bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-xs text-neutral-200 max-w-[220px]">
      <p className="font-medium text-neutral-100 truncate">{d?.book_title}</p>
      <p className="text-neutral-400 mb-1 truncate">{d?.chapter_title}</p>
      {payload.map(p => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.name}: {Number(p.value).toFixed(3)}
        </p>
      ))}
    </div>
  )
}

export default function SentimentChart({ onContextChange }) {
  const { selectedBooks } = useFilter()
  const [data, setData] = useState([])
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSentiment()
      .then(records => {
        const uniqueBooks = [...new Set(records.map(r => r.book))].sort((a, b) => a - b)
        const sorted = [...records].sort((a, b) => a.book - b.book || a.chapter - b.chapter)
        const rows = sorted.map((r, i) => ({
          index: i,
          [`book${r.book}`]: r.compound,
          book: r.book,
          chapter: r.chapter,
          book_title: r.book_title,
          chapter_title: r.chapter_title,
        }))
        setBooks(uniqueBooks)
        setData(rows)
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!books.length) return
    onContextChange?.({
      chart: 'sentiment',
      books,
      selectedBooks: [...selectedBooks].sort((a, b) => a - b),
      chapterRange: [0, data.length - 1],
      dataPointCount: data.length,
    })
  }, [selectedBooks, books, data.length, onContextChange])

  const visibleData = useMemo(() => {
    const filtered = data.filter(row =>
      selectedBooks.some(b => row[`book${b}`] !== undefined)
    )
    return filtered.map((row, i) => ({ ...row, displayIndex: i }))
  }, [data, selectedBooks])

  const yDomain = useMemo(() => {
    const values = []
    visibleData.forEach(row => {
      selectedBooks.forEach(b => {
        const v = row[`book${b}`]
        if (v !== undefined) values.push(v)
      })
    })
    if (!values.length) return [-0.1, 0.1]
    const min = Math.min(...values)
    const max = Math.max(...values)
    return [Math.round((min - 0.05) * 100) / 100, Math.round((max + 0.05) * 100) / 100]
  }, [visibleData, selectedBooks])

  if (loading) return <div className="flex items-center justify-center h-64 text-neutral-500 text-sm">Loading sentiment…</div>
  if (error) return <div className="flex items-center justify-center h-64 text-red-400 text-sm">Error: {error}</div>
  if (!selectedBooks.length) return <div className="flex items-center justify-center h-32 text-neutral-500 text-sm">No books selected</div>

  const chartHeight = Math.max(200, selectedBooks.length * 45 + 80)

  return (
    <ResponsiveContainer width="100%" height={chartHeight}>
      <LineChart data={visibleData} margin={{ top: 8, right: 16, bottom: 24, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={THEME.chart.grid} />
        <XAxis
          dataKey="displayIndex"
          tick={{ fill: THEME.chart.tick, fontSize: 11 }}
          label={{ value: 'Chapter (series)', position: 'insideBottom', offset: -12, fill: THEME.chart.label, fontSize: 11 }}
        />
        <YAxis
          domain={yDomain}
          tick={{ fill: THEME.chart.tick, fontSize: 11 }}
          label={{ value: 'Sentiment', angle: -90, position: 'insideLeft', offset: 12, fill: THEME.chart.label, fontSize: 11 }}
        />
        <ReferenceLine y={0} stroke="#525252" strokeDasharray="4 4" />
        <Tooltip content={<CustomTooltip />} />
        <Legend formatter={v => <span className="text-xs text-neutral-400">{v.replace('book', 'Book ')}</span>} />
        {books.filter(b => selectedBooks.includes(b)).map(b => (
          <Line
            key={b}
            type="monotone"
            dataKey={`book${b}`}
            name={`book${b}`}
            stroke={BOOK_COLORS[books.indexOf(b) % BOOK_COLORS.length]}
            dot={false}
            strokeWidth={1.5}
            connectNulls
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
