export default function SourceCards({ sources }) {
  if (!sources?.length) return null
  return (
    <div className="flex gap-1.5 flex-wrap mt-1.5 max-w-[85%]">
      {sources.map((s, i) => (
        <div
          key={i}
          title={`${s.book_title} — ${s.chapter_title}`}
          className="bg-neutral-900 border border-neutral-700 rounded px-2 py-1 text-xs max-w-[140px]"
        >
          <span className="block text-neutral-400 font-medium truncate">{s.book_title}</span>
          <span className="block text-neutral-600 truncate">{s.chapter_title}</span>
        </div>
      ))}
    </div>
  )
}
