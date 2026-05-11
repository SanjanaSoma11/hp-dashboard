import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { fetchWordCount } from '../../api/story'

function aggregate(records) {
  const totals = {}
  records.forEach(({ book, word_count }) => {
    totals[book] = (totals[book] || 0) + word_count
  })
  return Object.entries(totals)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([book, total]) => ({ book: `Book ${book}`, bookNum: Number(book), total }))
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-xs text-neutral-200">
      <p>{label}</p>
      <p className="text-violet-400">{payload[0].value.toLocaleString()} words</p>
    </div>
  )
}

export default function WordCountChart({ onContextChange }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchWordCount()
      .then(records => {
        const aggregated = aggregate(records)
        setData(aggregated)
        onContextChange?.({
          chart: 'wordcount',
          books: aggregated.map(d => d.bookNum),
          totalWords: aggregated.reduce((sum, d) => sum + d.total, 0),
        })
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64 text-neutral-500 text-sm">Loading word counts…</div>
  if (error) return <div className="flex items-center justify-center h-64 text-red-400 text-sm">Error: {error}</div>

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
        <XAxis dataKey="book" tick={{ fill: '#737373', fontSize: 11 }} />
        <YAxis tickFormatter={v => `${(v / 1000).toFixed(0)}k`} tick={{ fill: '#737373', fontSize: 11 }} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="total" radius={[3, 3, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill="#7c3aed" />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
