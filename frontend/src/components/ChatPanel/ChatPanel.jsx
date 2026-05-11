import { useState, useRef, useEffect } from 'react'
import { streamChat } from '../../api/chat'

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
        <div
          key={i}
          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[85%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
              msg.role === 'user'
                ? 'bg-violet-600 text-white'
                : 'bg-neutral-800 text-neutral-100'
            }`}
          >
            {msg.content}
          </div>
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

  async function handleSend() {
    const question = input.trim()
    if (!question || streaming) return

    setInput('')
    setError(null)
    setMessages(prev => [...prev, { role: 'user', content: question }])
    setStreaming(true)

    try {
      const stream = await streamChat(question, chartContext)
      const reader = stream.getReader()
      const decoder = new TextDecoder()

      setMessages(prev => [...prev, { role: 'assistant', content: '' }])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        setMessages(prev => {
          const updated = [...prev]
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: updated[updated.length - 1].content + chunk,
          }
          return updated
        })
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
      <div className="px-4 py-3 border-b border-neutral-800">
        <span className="text-sm font-medium text-neutral-300">Chat</span>
      </div>

      <MessageList messages={messages} />

      {error && (
        <div className="mx-4 mb-2 px-3 py-2 rounded bg-red-900/40 text-red-400 text-xs">
          {error}
        </div>
      )}

      <div className="p-3 border-t border-neutral-800 flex gap-2">
        <input
          className="flex-1 bg-neutral-800 text-neutral-100 text-sm rounded px-3 py-2 placeholder-neutral-500 outline-none focus:ring-1 focus:ring-violet-500 disabled:opacity-50"
          placeholder="Ask a question about the story..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={streaming}
        />
        <button
          onClick={handleSend}
          disabled={streaming || !input.trim()}
          className="px-3 py-2 rounded bg-violet-600 text-white text-sm font-medium hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {streaming ? '...' : 'Send'}
        </button>
      </div>
    </div>
  )
}
