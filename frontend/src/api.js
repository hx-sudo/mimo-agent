import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export function fetchModels() {
  return api.get('/models').then(r => r.data)
}

export function sendMessage(message, messages, model, images = []) {
  return api.post('/chat', { message, messages, model, images }).then(r => r.data)
}

export function fetchConversations() {
  return api.get('/conversations').then(r => r.data.conversations)
}

export function loadConversation(id) {
  return api.get(`/conversations/${id}`).then(r => r.data)
}

export function saveConversation(id, title, messages, model) {
  return api.post('/conversations', { id, title, messages, model }).then(r => r.data)
}

export function deleteConversation(id) {
  return api.delete(`/conversations/${id}`).then(r => r.data)
}
