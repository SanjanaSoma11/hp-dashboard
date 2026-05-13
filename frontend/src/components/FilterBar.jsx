import { useFilter } from '../context/FilterContext'

const ALL_BOOKS = [1, 2, 3, 4, 5, 6, 7]

export default function FilterBar() {
  const { selectedBooks, setSelectedBooks } = useFilter()
  const selectedSet = new Set(selectedBooks)

  function toggleBook(book) {
    const next = new Set(selectedSet)
    next.has(book) ? next.delete(book) : next.add(book)
    setSelectedBooks([...next].sort((a, b) => a - b))
  }

  function selectAll() {
    setSelectedBooks([...ALL_BOOKS])
  }

  function clearAll() {
    setSelectedBooks([])
  }

  const allSelected = selectedBooks.length === ALL_BOOKS.length
  const noneSelected = selectedBooks.length === 0

  return (
    <div className="flex items-center gap-3 px-6 py-2.5 border-b border-neutral-800 bg-neutral-950 shrink-0">
      <span className="text-xs text-neutral-500 font-medium shrink-0">Books:</span>
      <div className="flex gap-1.5">
        {ALL_BOOKS.map(book => (
          <button
            key={book}
            onClick={() => toggleBook(book)}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              selectedSet.has(book)
                ? 'bg-violet-600 text-white'
                : 'bg-neutral-800 text-neutral-400 hover:bg-neutral-700 hover:text-neutral-200'
            }`}
          >
            {book}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-2 ml-auto shrink-0">
        <button
          onClick={selectAll}
          disabled={allSelected}
          className="text-xs text-neutral-500 hover:text-neutral-300 disabled:opacity-30 transition-colors"
        >
          All
        </button>
        <span className="text-neutral-700 text-xs">·</span>
        <button
          onClick={clearAll}
          disabled={noneSelected}
          className="text-xs text-neutral-500 hover:text-neutral-300 disabled:opacity-30 transition-colors"
        >
          Clear
        </button>
      </div>
    </div>
  )
}
