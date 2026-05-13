import { useState, useEffect, useMemo } from 'react'
import { fetchMentions } from '../../api/characters'
import { useFilter } from '../../context/FilterContext'

const ALL_BOOKS = [1, 2, 3, 4, 5, 6, 7]
const BOOK_LABELS = { 1: 'B1', 2: 'B2', 3: 'B3', 4: 'B4', 5: 'B5', 6: 'B6', 7: 'B7' }
const TOP_N = 15

// Color scale: dark neutral → violet-600 (124, 58, 237)
const LOW  = [25, 25, 35]
const HIGH = [124, 58, 237]

function lerpColor([r1, g1, b1], [r2, g2, b2], t) {
  return `rgb(${Math.round(r1 + (r2 - r1) * t)},${Math.round(g1 + (g2 - g1) * t)},${Math.round(b1 + (b2 - b1) * t)})`
}

export default function CharacterHeatmap() {
  const [raw, setRaw]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState(false)
  const { selectedBooks }   = useFilter()

  useEffect(() => {
    fetchMentions()
      .then(d => { setRaw(d); setLoading(false) })
      .catch(() => { setError(true); setLoading(false) })
  }, [])

  const { characters, matrix, maxVal, visibleBooks } = useMemo(() => {
    if (!raw) return { characters: [], matrix: {}, maxVal: 1, visibleBooks: ALL_BOOKS }

    const books = selectedBooks.length > 0 ? selectedBooks : ALL_BOOKS

    // Rank characters by total mention_count across all books (stable ordering)
    const totalMentions = {}
    raw.forEach(r => { totalMentions[r.character] = (totalMentions[r.character] || 0) + r.mention_count })
    const topChars = Object.entries(totalMentions)
      .sort((a, b) => b[1] - a[1])
      .slice(0, TOP_N)
      .map(([name]) => name)
    const charSet = new Set(topChars)

    // Average mentions_per_1k_words per (character, book) across chapters
    const sums = {}, counts = {}
    raw.forEach(r => {
      if (!charSet.has(r.character)) return
      const k = `${r.character}|${r.book}`
      sums[k] = (sums[k] || 0) + r.mentions_per_1k_words
      counts[k] = (counts[k] || 0) + 1
    })

    let maxVal = 0
    const matrix = {}
    topChars.forEach(char => {
      matrix[char] = {}
      books.forEach(book => {
        const k = `${char}|${book}`
        const val = counts[k] ? sums[k] / counts[k] : 0
        matrix[char][book] = val
        if (val > maxVal) maxVal = val
      })
    })

    return { characters: topChars, matrix, maxVal: maxVal || 1, visibleBooks: books }
  }, [raw, selectedBooks])

  if (loading) return <div className="text-sm text-neutral-500 py-4 animate-pulse">Loading…</div>
  if (error)   return <div className="text-sm text-red-500/70 py-4">Failed to load character data.</div>
  if (visibleBooks.length === 0) return <div className="text-sm text-neutral-600 py-4">No books selected.</div>

  return (
    <div className="overflow-x-auto">
      <table className="text-xs border-collapse w-full">
        <thead>
          <tr>
            <th className="text-left text-neutral-500 font-medium pr-6 pb-2 whitespace-nowrap">Character</th>
            {visibleBooks.map(b => (
              <th key={b} className="text-neutral-500 font-medium px-2 pb-2 text-center min-w-[40px]">
                {BOOK_LABELS[b]}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {characters.map(char => (
            <tr key={char}>
              <td className="text-neutral-300 pr-6 py-[3px] whitespace-nowrap">{char}</td>
              {visibleBooks.map(book => {
                const val = matrix[char]?.[book] ?? 0
                const t   = val / maxVal
                return (
                  <td
                    key={book}
                    title={`${char} — Book ${book}: ${val.toFixed(2)}/1k words`}
                    style={{ backgroundColor: lerpColor(LOW, HIGH, t) }}
                    className="px-2 py-[3px] text-center text-neutral-200"
                  >
                    {val > 0.05 ? val.toFixed(1) : ''}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
