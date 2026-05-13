import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import { fetchRelationships } from '../../api/characters'
import { useFilter } from '../../context/FilterContext'
import { COLORS } from '../../utils/colors'
import NodeStatsPanel from './NodeStatsPanel'

const MIN_RADIUS = 3
const MAX_RADIUS = 12

export default function RelationshipGraph() {
  const { selectedBooks } = useFilter()
  const [allNodes, setAllNodes] = useState([])
  const [allEdges, setAllEdges] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [edgeThreshold, setEdgeThreshold] = useState(0)
  const [thresholdReady, setThresholdReady] = useState(false)
  const [selectedNode, setSelectedNode] = useState(null)
  const containerRef = useRef(null)
  const [graphWidth, setGraphWidth] = useState(0)

  useEffect(() => {
    fetchRelationships()
      .then(data => {
        setAllNodes(data.nodes)
        setAllEdges(data.edges)
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  // Set default edge threshold to median weight once data loads
  useEffect(() => {
    if (!thresholdReady && allEdges.length > 0) {
      const sorted = [...allEdges].map(e => e.weight).sort((a, b) => a - b)
      const median = sorted[Math.floor(sorted.length / 2)]
      setEdgeThreshold(median)
      setThresholdReady(true)
    }
  }, [allEdges, thresholdReady])

  useEffect(() => {
    if (!containerRef.current) return
    const ro = new ResizeObserver(entries => {
      setGraphWidth(entries[0].contentRect.width)
    })
    ro.observe(containerRef.current)
    return () => ro.disconnect()
  }, [])

  const { graphData, colorMap, maxMentions, minMentions, maxWeight, visibleIds } = useMemo(() => {
    if (!allNodes.length) return {
      graphData: { nodes: [], links: [] }, colorMap: new Map(),
      maxMentions: 1, minMentions: 0, maxWeight: 1, visibleIds: new Set(),
    }

    const visibleNodes = allNodes.filter(n =>
      n.books.some(b => selectedBooks.includes(b))
    )
    const ids = new Set(visibleNodes.map(n => n.id))

    const visibleEdges = allEdges.filter(
      e => ids.has(e.source) && ids.has(e.target) && e.weight >= edgeThreshold
    )

    const nodeNames = visibleNodes.map(n => n.id).sort()
    const cm = new Map(nodeNames.map((name, i) => [name, COLORS[i % COLORS.length]]))
    const mentions = visibleNodes.map(n => n.mention_count)
    const maxM = Math.max(...mentions, 1)
    const minM = Math.min(...mentions, 0)
    const mw = Math.max(...allEdges.map(e => e.weight), 1)

    return {
      graphData: {
        nodes: visibleNodes.map(n => ({
          id: n.id,
          mention_count: n.mention_count,
          degree: n.degree,
          pagerank: n.pagerank,
        })),
        links: visibleEdges.map(e => ({ source: e.source, target: e.target, weight: e.weight })),
      },
      colorMap: cm,
      maxMentions: maxM,
      minMentions: minM,
      maxWeight: mw,
      visibleIds: ids,
    }
  }, [allNodes, allEdges, selectedBooks, edgeThreshold])

  const nodeCanvasObject = useCallback((node, ctx) => {
    const color = colorMap.get(node.id) || COLORS[0]
    const range = maxMentions - minMentions || 1
    const r = MIN_RADIUS + ((node.mention_count - minMentions) / range) * (MAX_RADIUS - MIN_RADIUS)
    const isSelected = selectedNode?.id === node.id
    ctx.beginPath()
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI)
    ctx.fillStyle = color
    ctx.fill()
    if (isSelected) {
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 1.5
      ctx.stroke()
    }
    ctx.font = '10px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'top'
    ctx.fillStyle = '#a3a3a3'
    ctx.fillText(node.id, node.x, node.y + r + 2)
  }, [colorMap, maxMentions, minMentions, selectedNode])

  const nodePointerAreaPaint = useCallback((node, color, ctx) => {
    const range = maxMentions - minMentions || 1
    const r = MIN_RADIUS + ((node.mention_count - minMentions) / range) * (MAX_RADIUS - MIN_RADIUS)
    ctx.fillStyle = color
    ctx.beginPath()
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI)
    ctx.fill()
  }, [maxMentions, minMentions])

  const linkWidth = useCallback(link => 0.5 + (link.weight / maxWeight) * 3.5, [maxWeight])

  const onNodeClick = useCallback((node) => {
    const full = allNodes.find(n => n.id === node.id) || null
    setSelectedNode(prev => prev?.id === node.id ? null : full)
  }, [allNodes])

  const isEmpty = !selectedBooks.length || (!loading && !error && graphData.nodes.length === 0)

  return (
    <div>
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
        {isEmpty && !loading && !error && (
          <div className="flex items-center justify-center h-full text-neutral-500 text-sm">
            No characters in selected books
          </div>
        )}
        {!loading && !error && !isEmpty && graphWidth > 0 && (
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
            onNodeClick={onNodeClick}
          />
        )}
      </div>

      {/* Edge weight threshold slider */}
      {!loading && !error && thresholdReady && (
        <div className="mt-3 flex items-center gap-3">
          <span className="text-xs text-neutral-500 shrink-0">Edge threshold</span>
          <input
            type="range"
            min={0}
            max={maxWeight}
            step={1}
            value={edgeThreshold}
            onChange={e => {
              setEdgeThreshold(Number(e.target.value))
              setSelectedNode(null)
            }}
            className="flex-1 accent-violet-500"
          />
          <span className="text-xs text-neutral-400 w-16 text-right">
            ≥ {edgeThreshold} ({graphData.links.length} edges)
          </span>
        </div>
      )}

      {/* Node stats panel */}
      {selectedNode && (
        <NodeStatsPanel
          node={selectedNode}
          allEdges={allEdges}
          visibleIds={visibleIds}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  )
}
