import type { ConversationMeta, ConversationCreate, ConversationUpdate, ConversationMessagesResponse, ConversationMessage } from '@/types/conversation'

const API_BASE = '/api/conversation'

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
  return response.json()
}

export const conversationService = {
  async getConversations(mode?: string): Promise<ConversationMeta[]> {
    const url = mode ? `${API_BASE}?mode=${mode}` : `${API_BASE}`
    return fetchJson<ConversationMeta[]>(url)
  },

  async createConversation(data?: ConversationCreate): Promise<ConversationMeta> {
    return fetchJson<ConversationMeta>(`${API_BASE}`, {
      method: 'POST',
      body: JSON.stringify(data || {}),
    })
  },

  async getLatestConversationByMode(mode: string): Promise<ConversationMeta | null> {
    try {
      return await fetchJson<ConversationMeta>(`${API_BASE}/latest?mode=${mode}`)
    } catch {
      return null
    }
  },

  async getConversationMessages(sessionId: string): Promise<ConversationMessagesResponse> {
    return fetchJson<ConversationMessagesResponse>(`${API_BASE}/${sessionId}/messages`)
  },

  async addMessage(sessionId: string, message: ConversationMessage): Promise<ConversationMessage> {
    return fetchJson<ConversationMessage>(`${API_BASE}/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify(message),
    })
  },

  async updateConversation(sessionId: string, update: ConversationUpdate): Promise<ConversationMeta> {
    return fetchJson<ConversationMeta>(`${API_BASE}/${sessionId}`, {
      method: 'PUT',
      body: JSON.stringify(update),
    })
  },

  async deleteConversation(sessionId: string): Promise<boolean> {
    const result = await fetchJson<{ success: boolean }>(`${API_BASE}/${sessionId}`, {
      method: 'DELETE',
    })
    return result.success
  },

  async searchConversations(query: string): Promise<ConversationMeta[]> {
    return fetchJson<ConversationMeta[]>(`${API_BASE}/search?query=${encodeURIComponent(query)}`)
  },
}
