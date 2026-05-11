import { useState, useCallback } from 'react'
import { StoryArc } from './components/StoryArc'
import { CharacterIntel } from './components/CharacterIntel'
import ChatPanel from './components/ChatPanel/ChatPanel'
import './index.css'

export default function App() {
  const [activeSection] = useState('story-arc')
  const [chartContext, setChartContext] = useState({ charts: [] })

  const handleContextChange = useCallback((ctx) => {
    setChartContext(prev => ({ ...prev, [ctx.chart]: ctx }))
  }, [])

  return (
    <div className="flex h-screen bg-[#0f0f0f] overflow-hidden">
      <main className="w-3/4 overflow-y-auto">
        {activeSection === 'story-arc' && <StoryArc onContextChange={handleContextChange} />}
        <CharacterIntel onContextChange={handleContextChange} />
      </main>
      <aside className="w-1/4 flex flex-col">
        <ChatPanel chartContext={chartContext} />
      </aside>
    </div>
  )
}
