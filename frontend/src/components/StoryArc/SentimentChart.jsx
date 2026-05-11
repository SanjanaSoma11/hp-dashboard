import { useState, useEffect } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { fetchSentiment } from '../../api/story'

const BOOK_COLORS = ['#818cf8', '#34d399', '#fb923c', '#f472b6', '#facc15', '#38bdf8', '#a78bfa']

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div className="bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-xs text-neutral-200">
      <p>Book {d?.book} · Chapter {d?.chapter}</p>
      {payload.map(p => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.name}: {Number(p.value).toFixed(3)}
        </p>
      ))}
    </div>
  )
}

export default function SentimentChart({ onContextChange }) {
  const [data, setData] = useState([])
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSentiment()
      .then(records => {
        const uniqueBooks = [...new Set(records.map(r => r.book))].sort((a, b) => a - b)
        const sorted = [...records].sort((a, b) => a.book - b.book || a.chapter - b.chapter)
        const rows = sorted.map((r, i) => ({ index: i, [`book${r.book}`]: r.compound, book: r.book, chapter: r.chapter }))
        setBooks(uniqueBooks)
        setData(rows)
        onContextChange?.({
          chart: 'sentiment',
          books: uniqueBooks,
          chapterRange: [0, rows.length - 1],
          dataPointCount: records.length,
        })
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64 text-neutral-500 text-sm">Loading sentiment…</div>
  if (error) return <div className="flex items-center justify-center h-64 text-red-400 text-sm">Error: {error}</div>

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
        <XAxis dataKey="index" tick={{ fill: '#737373', fontSize: 11 }} label={{ value: 'Chapter (global)', position: 'insideBottom', offset: -4, fill: '#525252', fontSize: 11 }} />
        <YAxis domain={[-1, 1]} tick={{ fill: '#737373', fontSize: 11 }} />
        <ReferenceLine y={0} stroke="#525252" strokeDasharray="4 4" />
        <Tooltip content={<CustomTooltip />} />
        <Legend formatter={v => <span className="text-xs text-neutral-400">{v.replace('book', 'Book ')}</span>} />
        {books.map((b, i) => (
          <Line
            key={b}
            type="monotone"
            dataKey={`book${b}`}
            name={`book${b}`}
            stroke={BOOK_COLORS[i % BOOK_COLORS.length]}
            dot={false}
            strokeWidth={1.5}
            connectNulls
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
