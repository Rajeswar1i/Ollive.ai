import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
})

export const createConversation = () =>
  api.post('/conversations').then(r => r.data)

export const listConversations = () =>
  api.get('/conversations').then(r => r.data)

export const getConversation = (id: string) =>
  api.get(`/conversations/${id}`).then(r => r.data)

export const cancelConversation = (id: string) =>
  api.delete(`/conversations/${id}/cancel`).then(r => r.data)

export const sendMessage = (conversationId: string, message: string) =>
  api.post(`/chat/${conversationId}`, { message }).then(r => r.data)

export const deleteConversation = (id: string) =>
  api.delete(`/conversations/${id}`)

export const getMetrics = () =>
  api.get('/metrics').then(r => r.data)
