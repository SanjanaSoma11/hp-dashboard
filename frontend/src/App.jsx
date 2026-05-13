import { useState, useCallback } from 'react'
import { StoryArc } from './components/StoryArc'
import { CharacterIntel } from './components/CharacterIntel'
import { OverviewPage } from './components/Overview'
import ChatPanel from './components/ChatPanel/ChatPanel'
import { FilterProvider, useFilter } from './context/FilterContext'
import FilterBar from './components/FilterBar'
import './index.css'

const TABS = [
  { id: 'overview',    label: 'Overview' },
  { id: 'story',       label: 'Story Arc' },
  { id: 'characters',  label: 'Character Intel' },
]

function TabBar({ active, onChange }) {
  return (
    <div className="flex border-b border-neutral-800 bg-neutral-950 shrink-0">
      {TABS.map(tab => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`px-5 py-3 text-sm font-medium transition-colors border-b-2 -mb-px ${
            active === tab.id
              ? 'border-violet-500 text-violet-400'
              : 'border-transparent text-neutral-500 hover:text-neutral-300'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}

function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const [chartContext, setChartContext] = useState({})
  const { selectedBooks } = useFilter()

  const handleContextChange = useCallback((ctx) => {
    setChartContext(prev => ({ ...prev, [ctx.chart]: ctx }))
  }, [])

  const fullContext = {
    globalFilters: { selectedBooks },
    charts: chartContext,
  }

  return (
    <div className="flex h-screen bg-[#0f1117] text-neutral-100 overflow-hidden">
      <main className="w-3/4 flex flex-col overflow-hidden">
        <TabBar active={activeTab} onChange={setActiveTab} />
        <FilterBar />
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'overview'    && <OverviewPage />}
          {activeTab === 'story'       && <StoryArc onContextChange={handleContextChange} />}
          {activeTab === 'characters'  && <CharacterIntel onContextChange={handleContextChange} />}
        </div>
      </main>
      <aside className="w-1/4 flex flex-col">
        <ChatPanel chartContext={fullContext} />
      </aside>
    </div>
  )
}

export default function App() {
  return (
    <FilterProvider>
      <Dashboard />
    </FilterProvider>
  )
}
