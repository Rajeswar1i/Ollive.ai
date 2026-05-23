import type { Message } from '../types'

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'
  return (
    <div style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', marginBottom: 14 }}>
      <div style={{
        maxWidth: '70%',
        padding: '11px 16px',
        borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
        background: isUser ? '#2563eb' : '#1e293b',
        color: '#f1f5f9',
        fontSize: 14,
        lineHeight: 1.6,
        border: isUser ? 'none' : '1.5px solid #334155',
        boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
      }}>
        {message.content}
      </div>
    </div>
  )
}
