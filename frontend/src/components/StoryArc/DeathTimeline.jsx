import { useState, useEffect, useMemo } from 'react'
import {
  ScatterChart, Scatter, XAxis, YAxis, Tooltip,
  ReferenceLine, ResponsiveContainer, Cell,
} from 'recharts'
import { fetchDeaths } from '../../api/story'
import { useFilter } from '../../context/FilterContext'
import { COLORS } from '../../utils/colors'
import { THEME } from '../../utils/theme'

const BOOK_COLORS = COLORS.slice(0, 7)

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div className="bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-xs text-neutral-200 max-w-[220px]">
      <p className="font-medium text-neutral-100">{d?.character}</p>
      <p className="text-neutral-300 truncate">{d?.book_title}</p>
      <p className="text-neutral-400 truncate">{d?.chapter_title}</p>
    </div>
  )
}

function CustomDot({ cx, cy, payload }) {
  const color = BOOK_COLORS[(payload.book - 1) % BOOK_COLORS.length]
  return (
    <g>
      <circle cx={cx} cy={cy} r={5} fill={color} stroke="#1a1a1a" strokeWidth={1.5} />
      <text x={cx} y={cy - 10} textAnchor="middle" fontSize={9} fill="#a3a3a3">
        {payload.character.split(' ').pop()}
      </text>
    </g>
  )
}

export default function DeathTimeline() {
  const { selectedBooks } = useFilter()
  const [allData, setAllData] = useState([])
  const [allBoundaries, setAllBoundaries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDeaths()
      .then(records => {
        setAllData(records.map(r => ({ ...r, y: 0 })))
        const boundaries = []
        const seen = new Set()
        records
          .slice()
          .sort((a, b) => a.chapter_seq_index - b.chapter_seq_index)
          .forEach(r => {
            if (!seen.has(r.book)) {
              seen.add(r.book)
              if (r.book > 1) boundaries.push({ book: r.book, x: r.chapter_seq_index })
            }
          })
        setAllBoundaries(boundaries)
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const data = useMemo(
    () => allData.filter(r => selectedBooks.includes(r.book)),
    [allData, selectedBooks]
  )

  const bookBoundaries = useMemo(
    () => allBoundaries.filter(b => selectedBooks.includes(b.book)),
    [allBoundaries, selectedBooks]
  )

  if (loading) return <div className="flex items-center justify-center h-32 text-neutral-500 text-sm">Loading deaths…</div>
  if (error) return <div className="flex items-center justify-center h-32 text-red-400 text-sm">Error: {error}</div>
  if (!selectedBooks.length || !data.length) return <div className="flex items-center justify-center h-16 text-neutral-500 text-sm">No deaths in selected books</div>

  return (
    <div>
      <div className="flex gap-4 mb-3 flex-wrap">
        {BOOK_COLORS.map((color, i) => (
          <span key={i} className={`flex items-center gap-1.5 text-xs transition-opacity ${selectedBooks.includes(i + 1) ? 'text-neutral-400' : 'text-neutral-700'}`}>
            <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ background: color }} />
            Book {i + 1}
          </span>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={110}>
        <ScatterChart margin={{ top: 24, right: 24, bottom: 16, left: 24 }}>
          <XAxis
            dataKey="chapter_seq_index"
            type="number"
            tick={{ fill: THEME.chart.tick, fontSize: 11 }}
            label={{ value: 'Chapter (series)', position: 'insideBottom', offset: -4, fill: THEME.chart.label, fontSize: 11 }}
            domain={['dataMin - 5', 'dataMax + 5']}
          />
          <YAxis dataKey="y" type="number" hide domain={[-1, 1]} />
          {bookBoundaries.map(b => (
            <ReferenceLine
              key={b.book}
              x={b.x}
              stroke="#404040"
              strokeDasharray="4 4"
              label={{ value: `B${b.book}`, position: 'top', fill: '#525252', fontSize: 9 }}
            />
          ))}
          <Tooltip content={<CustomTooltip />} />
          <Scatter data={data} shape={<CustomDot />}>
            {data.map((d, i) => (
              <Cell key={i} fill={BOOK_COLORS[(d.book - 1) % BOOK_COLORS.length]} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}
