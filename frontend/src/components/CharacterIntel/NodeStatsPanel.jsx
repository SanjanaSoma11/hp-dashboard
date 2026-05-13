function StatRow({ label, value }) {
  return (
    <div className="flex justify-between items-baseline gap-4">
      <span className="text-xs text-neutral-500">{label}</span>
      <span className="text-xs font-medium text-neutral-200">{value}</span>
    </div>
  )
}

export default function NodeStatsPanel({ node, allEdges, visibleIds, onClose }) {
  if (!node) return null

  const neighbors = allEdges
    .filter(e =>
      (e.source === node.id || e.target === node.id) &&
      visibleIds.has(e.source) &&
      visibleIds.has(e.target)
    )
    .map(e => ({
      name: e.source === node.id ? e.target : e.source,
      weight: e.weight,
    }))
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 3)

  return (
    <div className="mt-3 rounded-lg border border-neutral-700 bg-neutral-900 p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-neutral-100">{node.id}</span>
        <button
          onClick={onClose}
          className="text-neutral-600 hover:text-neutral-400 text-xs leading-none"
          aria-label="Close"
        >
          ✕
        </button>
      </div>
      <div className="space-y-1.5">
        <StatRow label="Total mentions" value={node.mention_count.toLocaleString()} />
        <StatRow label="Degree" value={node.degree} />
        <StatRow label="PageRank" value={node.pagerank.toFixed(4)} />
      </div>
      {neighbors.length > 0 && (
        <div className="mt-3 pt-3 border-t border-neutral-800">
          <p className="text-xs text-neutral-500 mb-1.5">Top connections</p>
          {neighbors.map(n => (
            <div key={n.name} className="flex justify-between items-baseline">
              <span className="text-xs text-neutral-300">{n.name}</span>
              <span className="text-xs text-neutral-600">{n.weight} chapters</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
