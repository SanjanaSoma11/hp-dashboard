import { useState, useEffect, useRef, useMemo } from 'react'
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

function BookDropdown({ books, selected, onChange }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const allSelected = selected.size === books.length

  function toggleBook(book) {
    const next = new Set(selected)
    next.has(book) ? next.delete(book) : next.add(book)
    if (next.size === 0) onChange(new Set(books))
    else onChange(next)
  }

  function selectAll() {
    onChange(new Set(books))
    setOpen(false)
  }

  const label = allSelected
    ? 'All Books'
    : [...selected].sort((a, b) => a - b).map(b => `Book ${b}`).join(', ')

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-2 px-3 py-1.5 rounded bg-neutral-800 border border-neutral-700 text-xs text-neutral-300 hover:border-neutral-500 transition-colors"
      >
        <span className="max-w-[180px] truncate">{label}</span>
        <svg className={`w-3 h-3 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1 z-10 min-w-[140px] rounded border border-neutral-700 bg-neutral-900 shadow-xl py-1">
          <button
            onClick={selectAll}
            className={`w-full text-left px-3 py-1.5 text-xs transition-colors hover:bg-neutral-800 ${allSelected ? 'text-neutral-100' : 'text-neutral-400'}`}
          >
            All Books
          </button>
          <div className="border-t border-neutral-800 my-1" />
          {books.map(b => (
            <label key={b} className="flex items-center gap-2 px-3 py-1.5 text-xs text-neutral-300 hover:bg-neutral-800 cursor-pointer">
              <input
                type="checkbox"
                checked={selected.has(b)}
                onChange={() => toggleBook(b)}
                className="accent-indigo-400"
              />
              Book {b}
            </label>
          ))}
        </div>
      )}
    </div>
  )
}

export default function SentimentChart({ onContextChange }) {
  const [data, setData] = useState([])
  const [books, setBooks] = useState([])
  const [selectedBooks, setSelectedBooks] = useState(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSentiment()
      .then(records => {
        const uniqueBooks = [...new Set(records.map(r => r.book))].sort((a, b) => a - b)
        const sorted = [...records].sort((a, b) => a.book - b.book || a.chapter - b.chapter)
        const rows = sorted.map((r, i) => ({ index: i, [`book${r.book}`]: r.compound, book: r.book, chapter: r.chapter }))
        setBooks(uniqueBooks)
        setSelectedBooks(new Set(uniqueBooks))
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
      [...selectedBooks].some(b => row[`book${b}`] !== undefined)
    )
    return filtered.map((row, i) => ({ ...row, displayIndex: i }))
  }, [data, selectedBooks])

  const yDomain = useMemo(() => {
    const values = []
    visibleData.forEach(row => {
      ;[...selectedBooks].forEach(b => {
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

  const selectedCount = selectedBooks.size
  const chartHeight = Math.max(200, selectedCount * 45 + 80)

  return (
    <div>
      <div className="flex justify-end mb-2">
        <BookDropdown books={books} selected={selectedBooks} onChange={setSelectedBooks} />
      </div>
      <ResponsiveContainer width="100%" height={chartHeight}>
        <LineChart data={visibleData} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
          <XAxis dataKey="displayIndex" tick={{ fill: '#737373', fontSize: 11 }} label={{ value: 'Chapter', position: 'insideBottom', offset: -4, fill: '#525252', fontSize: 11 }} />
          <YAxis domain={yDomain} tick={{ fill: '#737373', fontSize: 11 }} />
          <ReferenceLine y={0} stroke="#525252" strokeDasharray="4 4" />
          <Tooltip content={<CustomTooltip />} />
          <Legend formatter={v => <span className="text-xs text-neutral-400">{v.replace('book', 'Book ')}</span>} />
          {books.filter(b => selectedBooks.has(b)).map((b, i) => (
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
    </div>
  )
}
