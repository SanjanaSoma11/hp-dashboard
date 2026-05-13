import { useState, useRef, useEffect } from 'react'
import { streamChat } from '../../api/chat'
import { useFilter } from '../../context/FilterContext'
import SourceCards from './SourceCards'

const ALL_BOOKS = [1, 2, 3, 4, 5, 6, 7]

const SUGGESTED_PROMPTS = [
  'Which character is mentioned most in Book 4?',
  'What is the most negative chapter in the series?',
  'Who is most connected to Harry Potter?',
  'What happens at the end of Book 6?',
  'How does Hermione\'s presence change across the books?',
  'Which book has the most deaths?',
]

function FilterIndicator({ selectedBooks }) {
  if (selectedBooks.length === ALL_BOOKS.length) return null
  const label = selectedBooks.length === 0
    ? 'No books selected'
    : `Filtering: Book ${selectedBooks.join(', ')}`
  return (
    <div className="px-4 py-1.5 border-b border-neutral-800 bg-violet-950/30 shrink-0">
      <span className="text-xs text-violet-400">{label}</span>
    </div>
  )
}

function MessageList({ messages }) {
  const bottomRef = useRef(null)
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <p className="text-neutral-500 text-xs text-center leading-relaxed">
          Ask anything about the Harry Potter story. Context from the visible charts is included automatically.
        </p>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {messages.map((msg, i) => (
        <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
          <div
            className={`max-w-[85%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
              msg.role === 'user'
                ? 'bg-violet-600 text-white'
                : 'bg-neutral-800 text-neutral-100'
            }`}
          >
            {msg.content}
          </div>
          {msg.role === 'assistant' && <SourceCards sources={msg.sources} />}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}

export default function ChatPanel({ chartContext }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState(null)
  const { selectedBooks } = useFilter()

  const lastAnswer = [...messages].reverse().find(m => m.role === 'assistant')?.content ?? ''

  function handleCopy() {
    if (lastAnswer) navigator.clipboard.writeText(lastAnswer)
  }

  function handleClear() {
    setMessages([])
    setInput('')
    setError(null)
  }

  async function handleSend(overrideQuestion) {
    const question = (overrideQuestion ?? input).trim()
    if (!question || streaming) return

    const history = messages.slice(-6)
    setInput('')
    setError(null)
    setMessages(prev => [...prev, { role: 'user', content: question }])
    setStreaming(true)

    try {
      const stream = await streamChat(question, chartContext, history)
      const reader = stream.getReader()
      const decoder = new TextDecoder()

      setMessages(prev => [...prev, { role: 'assistant', content: '', sources: [] }])

      let buffer = ''
      let sourcesFound = false

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })

        if (!sourcesFound) {
          buffer += chunk
          const nlIdx = buffer.indexOf('\n')
          if (nlIdx !== -1) {
            const firstLine = buffer.slice(0, nlIdx)
            const rest = buffer.slice(nlIdx + 1)
            sourcesFound = true
            let sources = []
            if (firstLine.startsWith('__SOURCES__:')) {
              try { sources = JSON.parse(firstLine.slice('__SOURCES__:'.length)) } catch {}
            }
            setMessages(prev => {
              const updated = [...prev]
              updated[updated.length - 1] = { ...updated[updated.length - 1], sources, content: rest }
              return updated
            })
          }
        } else {
          setMessages(prev => {
            const updated = [...prev]
            updated[updated.length - 1] = {
              ...updated[updated.length - 1],
              content: updated[updated.length - 1].content + chunk,
            }
            return updated
          })
        }
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setStreaming(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full bg-neutral-900 border-l border-neutral-800">
      {/* Header */}
      <div className="px-4 py-3 border-b border-neutral-800 flex items-center justify-between shrink-0">
        <span className="text-sm font-medium text-neutral-300">Chat</span>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            disabled={!lastAnswer}
            title="Copy last answer to clipboard"
            className="text-xs text-neutral-500 hover:text-neutral-300 disabled:opacity-30 transition-colors"
          >
            Copy
          </button>
          <span className="text-neutral-700 text-xs">·</span>
          <button
            onClick={handleClear}
            disabled={messages.length === 0}
            title="Clear conversation"
            className="text-xs text-neutral-500 hover:text-neutral-300 disabled:opacity-30 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Filter indicator */}
      <FilterIndicator selectedBooks={selectedBooks} />

      {/* Messages */}
      <MessageList messages={messages} />

      {/* Error */}
      {error && (
        <div className="mx-4 mb-2 px-3 py-2 rounded bg-red-900/40 text-red-400 text-xs shrink-0">
          {error}
        </div>
      )}

      {/* Suggested prompt chips */}
      <div className="px-3 pt-2 pb-1 flex flex-wrap gap-1.5 shrink-0">
        {SUGGESTED_PROMPTS.map((prompt, i) => (
          <button
            key={i}
            onClick={() => setInput(prompt)}
            disabled={streaming}
            className="text-xs bg-neutral-800 hover:bg-neutral-700 text-neutral-400 hover:text-neutral-200 border border-neutral-700 rounded px-2 py-1 transition-colors disabled:opacity-40 truncate max-w-full text-left"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="p-3 border-t border-neutral-800 flex gap-2 shrink-0">
        <input
          className="flex-1 bg-neutral-800 text-neutral-100 text-sm rounded px-3 py-2 placeholder-neutral-500 outline-none focus:ring-1 focus:ring-violet-500 disabled:opacity-50"
          placeholder="Ask a question about the story..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={streaming}
        />
        <button
          onClick={() => handleSend()}
          disabled={streaming || !input.trim()}
          className="px-3 py-2 rounded bg-violet-600 text-white text-sm font-medium hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {streaming ? '…' : 'Send'}
        </button>
      </div>
    </div>
  )
}
