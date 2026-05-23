import type { Conversation } from '../types'

interface Props {
  conversations: Conversation[]
  activeId: string | null
  onSelect: (id: string) => void
  onNew: () => void
  onCancel: (id: string) => void
  onDelete: (id: string) => void
}

export default function ConversationList({ conversations, activeId, onSelect, onNew, onCancel, onDelete }: Props) {
  return (
    <div style={{ width: 260, borderRight: '2px solid #1e293b', height: '100%', display: 'flex', flexDirection: 'column', background: '#0a0f1e' }}>
      <div style={{ padding: 16, borderBottom: '2px solid #1e293b' }}>
        <button
          onClick={onNew}
          style={{ width: '100%', padding: '8px 0', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}
        >
          + New Chat
        </button>
      </div>
      <div style={{ overflowY: 'auto', flex: 1 }}>
        {conversations.map(conv => (
          <div
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            style={{
              padding: '12px 16px',
              cursor: 'pointer',
              background: activeId === conv.id ? '#1e3a5f' : 'transparent',
              borderBottom: '1px solid #1e293b',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: conv.status === 'cancelled' ? '#94a3b8' : '#f1f5f9', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {conv.title ?? 'New conversation'}
              </div>
              <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>
                {conv.status === 'cancelled' ? 'Cancelled' : new Date(conv.created_at).toLocaleDateString()}
              </div>
            </div>
            <div style={{ display: 'flex', gap: 4, flexShrink: 0 }}>
              {conv.status === 'active' && (
                <button
                  onClick={e => { e.stopPropagation(); onCancel(conv.id) }}
                  style={{ fontSize: 11, color: '#f87171', background: 'none', border: 'none', cursor: 'pointer', padding: '2px 4px' }}
                >
                  Cancel
                </button>
              )}
              <button
                onClick={e => { e.stopPropagation(); onDelete(conv.id) }}
                style={{ fontSize: 11, color: '#64748b', background: 'none', border: 'none', cursor: 'pointer', padding: '2px 4px' }}
                title="Delete conversation"
              >
                🗑
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
