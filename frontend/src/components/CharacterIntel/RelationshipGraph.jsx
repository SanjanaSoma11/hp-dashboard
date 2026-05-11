import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import { fetchRelationships } from '../../api/characters'
import { COLORS } from '../../utils/colors'

export default function RelationshipGraph() {
  const [edges, setEdges] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const containerRef = useRef(null)
  const [graphWidth, setGraphWidth] = useState(0)

  useEffect(() => {
    fetchRelationships()
      .then(setEdges)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!containerRef.current) return
    const ro = new ResizeObserver(entries => {
      setGraphWidth(entries[0].contentRect.width)
    })
    ro.observe(containerRef.current)
    return () => ro.disconnect()
  }, [])

  const { graphData, colorMap, maxWeight } = useMemo(() => {
    if (!edges.length) return { graphData: { nodes: [], links: [] }, colorMap: new Map(), maxWeight: 1 }
    const nodeNames = [...new Set(edges.flatMap(e => [e.source, e.target]))].sort()
    const cm = new Map(nodeNames.map((name, i) => [name, COLORS[i % COLORS.length]]))
    const mw = Math.max(...edges.map(e => e.weight))
    return {
      graphData: {
        nodes: nodeNames.map(id => ({ id })),
        links: edges.map(e => ({ source: e.source, target: e.target, weight: e.weight })),
      },
      colorMap: cm,
      maxWeight: mw,
    }
  }, [edges])

  const nodeCanvasObject = useCallback((node, ctx) => {
    const color = colorMap.get(node.id) || COLORS[0]
    ctx.beginPath()
    ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI)
    ctx.fillStyle = color
    ctx.fill()
    ctx.font = '10px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'top'
    ctx.fillStyle = '#a3a3a3'
    ctx.fillText(node.id, node.x, node.y + 7)
  }, [colorMap])

  const nodePointerAreaPaint = useCallback((node, color, ctx) => {
    ctx.fillStyle = color
    ctx.beginPath()
    ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI)
    ctx.fill()
  }, [])

  const linkWidth = useCallback(link => 0.5 + (link.weight / maxWeight) * 3.5, [maxWeight])

  return (
    <div
      ref={containerRef}
      className="w-full rounded-lg overflow-hidden border border-neutral-800"
      style={{ height: 500, background: '#0f0f0f' }}
    >
      {loading && (
        <div className="flex items-center justify-center h-full text-neutral-500 text-sm">
          Loading relationships…
        </div>
      )}
      {error && (
        <div className="flex items-center justify-center h-full text-red-400 text-sm">
          Error: {error}
        </div>
      )}
      {!loading && !error && graphWidth > 0 && (
        <ForceGraph2D
          graphData={graphData}
          width={graphWidth}
          height={500}
          backgroundColor="#0f0f0f"
          nodeCanvasObject={nodeCanvasObject}
          nodeCanvasObjectMode={() => 'replace'}
          nodePointerAreaPaint={nodePointerAreaPaint}
          linkWidth={linkWidth}
          linkColor={() => '#404040'}
        />
      )}
    </div>
  )
}
