import { useState, useEffect, useMemo } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { fetchWordCount } from '../../api/story'
import { useFilter } from '../../context/FilterContext'
import { THEME } from '../../utils/theme'

const BOOK_TITLES = {
  1: "Philosopher's Stone",
  2: 'Chamber of Secrets',
  3: 'Prisoner of Azkaban',
  4: 'Goblet of Fire',
  5: 'Order of the Phoenix',
  6: 'Half-Blood Prince',
  7: 'Deathly Hallows',
}

function aggregate(records) {
  const totals = {}
  records.forEach(({ book, word_count }) => {
    totals[book] = (totals[book] || 0) + word_count
  })
  return Object.entries(totals)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([book, total]) => ({
      book: BOOK_TITLES[Number(book)] || `Book ${book}`,
      bookNum: Number(book),
      total,
    }))
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-xs text-neutral-200">
      <p className="font-medium text-neutral-100 mb-0.5">{label}</p>
      <p className="text-violet-400">{payload[0].value.toLocaleString()} words</p>
    </div>
  )
}

export default function WordCountChart({ onContextChange }) {
  const { selectedBooks } = useFilter()
  const [allRecords, setAllRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchWordCount()
      .then(records => setAllRecords(records))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const data = useMemo(() => {
    const filtered = allRecords.filter(r => selectedBooks.includes(r.book))
    return aggregate(filtered)
  }, [allRecords, selectedBooks])

  useEffect(() => {
    onContextChange?.({
      chart: 'wordcount',
      books: data.map(d => d.bookNum),
      totalWords: data.reduce((sum, d) => sum + d.total, 0),
    })
  }, [data, onContextChange])

  if (loading) return <div className="flex items-center justify-center h-64 text-neutral-500 text-sm">Loading word counts…</div>
  if (error) return <div className="flex items-center justify-center h-64 text-red-400 text-sm">Error: {error}</div>
  if (!selectedBooks.length || !data.length) return <div className="flex items-center justify-center h-32 text-neutral-500 text-sm">No books selected</div>

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={THEME.chart.grid} vertical={false} />
        <XAxis dataKey="book" tick={{ fill: THEME.chart.tick, fontSize: 10 }} />
        <YAxis
          tickFormatter={v => `${(v / 1000).toFixed(0)}k`}
          tick={{ fill: THEME.chart.tick, fontSize: 11 }}
          label={{ value: 'Words', angle: -90, position: 'insideLeft', offset: 12, fill: THEME.chart.label, fontSize: 11 }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="total" radius={[3, 3, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={THEME.accent.violet} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
