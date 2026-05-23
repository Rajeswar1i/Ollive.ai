import { useState, useRef, useEffect } from 'react'
import type { Conversation } from '../types'
import MessageBubble from './MessageBubble'
import { getConversation } from '../api/client'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

interface Props {
  conversation: Conversation | null
  onUpdate: (conv: Conversation) => void
}

export default function ChatWindow({ conversation, onUpdate }: Props) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [streamingText, setStreamingText] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation?.messages, streamingText])

  const handleSend = async () => {
    if (!input.trim() || !conversation || conversation.status === 'cancelled') return
    const text = input
    setInput('')
    setLoading(true)
    setStreamingText('')

    try {
      const response = await fetch(`${API_BASE}/chat/${conversation.id}/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let accumulated = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const lines = decoder.decode(value).split('\n')
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const payload = JSON.parse(line.slice(6))
          if (payload.chunk) {
            accumulated += payload.chunk
            setStreamingText(accumulated)
          }
          if (payload.error) {
            setStreamingText(`Error: ${payload.error}`)
          }
          if (payload.done) {
            const updated = await getConversation(conversation.id)
            onUpdate(updated)
            setStreamingText('')
          }
        }
      }
    } finally {
      setLoading(false)
    }
  }

  if (!conversation) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#475569', fontSize: 14, background: '#0f172a' }}>
        Select a conversation or start a new one
      </div>
    )
  }

  const isCancelled = conversation.status === 'cancelled'

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', background: '#0f172a' }}>
      {/* Header */}
      <div style={{
        padding: '14px 24px',
        borderBottom: '2px solid #1e293b',
        fontWeight: 700,
        fontSize: 15,
        color: '#f1f5f9',
        background: '#0a0f1e',
        display: 'flex',
        alignItems: 'center',
        gap: 10,
      }}>
        {conversation.title ?? 'New conversation'}
        {isCancelled && (
          <span style={{ fontSize: 11, color: '#f87171', background: '#2d1515', padding: '2px 8px', borderRadius: 20, fontWeight: 600 }}>
            Cancelled
          </span>
        )}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
        {conversation.messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {streamingText && (
          <MessageBubble message={{ id: 'streaming', role: 'assistant', content: streamingText, created_at: new Date().toISOString() }} />
        )}
        {loading && !streamingText && (
          <div style={{ color: '#475569', fontSize: 13, padding: '8px 0' }}>Thinking...</div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      {!isCancelled && (
        <div style={{
          padding: '14px 24px',
          borderTop: '2px solid #1e293b',
          display: 'flex',
          gap: 10,
          background: '#0a0f1e',
        }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Type a message..."
            style={{
              flex: 1,
              padding: '11px 16px',
              borderRadius: 10,
              border: '1.5px solid #1e293b',
              fontSize: 14,
              outline: 'none',
              background: '#1e293b',
              color: '#f1f5f9',
            }}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            style={{
              padding: '11px 24px',
              background: loading ? '#1e3a5f' : '#2563eb',
              color: '#fff',
              border: 'none',
              borderRadius: 10,
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 700,
              fontSize: 14,
              transition: 'background 0.2s',
            }}
          >
            Send
          </button>
        </div>
      )}
    </div>
  )
}
