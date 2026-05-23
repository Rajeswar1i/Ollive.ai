import { useEffect, useState } from 'react'
import type { Conversation } from '../types'
import { listConversations, createConversation, getConversation, cancelConversation, deleteConversation } from '../api/client'
import ConversationList from '../components/ConversationList'
import ChatWindow from '../components/ChatWindow'

export default function Home() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null)

  useEffect(() => {
    listConversations().then(setConversations)
  }, [])

  const handleNew = async () => {
    const conv = await createConversation()
    setConversations(prev => [conv, ...prev])
    setActiveConversation(conv)
  }

  const handleSelect = async (id: string) => {
    const conv = await getConversation(id)
    setActiveConversation(conv)
  }

  const handleCancel = async (id: string) => {
    const updated = await cancelConversation(id)
    setConversations(prev => prev.map(c => c.id === id ? updated : c))
    if (activeConversation?.id === id) setActiveConversation(updated)
  }

  const handleDelete = async (id: string) => {
    await deleteConversation(id)
    setConversations(prev => prev.filter(c => c.id !== id))
    if (activeConversation?.id === id) setActiveConversation(null)
  }

  const handleUpdate = (updated: Conversation) => {
    setActiveConversation(updated)
    setConversations(prev => prev.map(c => c.id === updated.id ? updated : c))
  }

  return (
    <div style={{ display: 'flex', flex: 1, overflow: 'hidden', fontFamily: 'Inter, sans-serif' }}>
      <ConversationList
        conversations={conversations}
        activeId={activeConversation?.id ?? null}
        onSelect={handleSelect}
        onNew={handleNew}
        onCancel={handleCancel}
        onDelete={handleDelete}
      />
      <ChatWindow conversation={activeConversation} onUpdate={handleUpdate} />
    </div>
  )
}
