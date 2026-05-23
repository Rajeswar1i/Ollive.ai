export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface Conversation {
  id: string
  title: string | null
  status: 'active' | 'cancelled'
  created_at: string
  messages: Message[]
}
