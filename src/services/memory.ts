import type {
  CoreMemory,
  CoreMemoryUpdate,
  RecallMemory,
  ArchivalMemory,
  ArchivalMemoryCreate,
  MemoryStats,
  MemorySearchResult,
  ProcessConversationRequest,
  MemoryExtractionResult,
  MemoryConfig,
  MemoryCategory,
  MemoryContextResult,
} from '@/types/memory'
import { API_BASE_URL } from './config'

const API_BASE = `${API_BASE_URL}/api/memory`

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  return response.json()
}

export const memoryService = {
  async getCoreMemory(): Promise<CoreMemory | null> {
    return fetchJson<CoreMemory>(`${API_BASE}/core`)
  },

  async updateCoreMemory(update: CoreMemoryUpdate): Promise<CoreMemory> {
    return fetchJson<CoreMemory>(`${API_BASE}/core`, {
      method: 'PUT',
      body: JSON.stringify(update),
    })
  },

  async getRecallMemories(limit: number = 100, offset: number = 0): Promise<RecallMemory[]> {
    return fetchJson<RecallMemory[]>(`${API_BASE}/recall?limit=${limit}&offset=${offset}`)
  },

  async deleteRecallMemory(memoryId: string): Promise<boolean> {
    const response = await fetchJson<{ success: boolean }>(`${API_BASE}/recall/${memoryId}`, {
      method: 'DELETE',
    })
    return response.success
  },

  async getArchivalMemories(limit: number = 100, offset: number = 0): Promise<ArchivalMemory[]> {
    return fetchJson<ArchivalMemory[]>(`${API_BASE}/archival?limit=${limit}&offset=${offset}`)
  },

  async createArchivalMemory(data: ArchivalMemoryCreate): Promise<ArchivalMemory> {
    const response = await fetchJson<{ memory_id: string; created_at: string; content_type: string }>(
      `${API_BASE}/archival`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    )
    return {
      memory_id: response.memory_id,
      user_id: '',
      content_type: data.content_type || 'note',
      title: data.title || '',
      content: data.content,
      source_papers: data.source_papers || [],
      tags: data.tags || [],
      created_at: response.created_at,
      last_accessed: response.created_at,
    }
  },

  async deleteArchivalMemory(memoryId: string): Promise<boolean> {
    const response = await fetchJson<{ success: boolean }>(`${API_BASE}/archival/${memoryId}`, {
      method: 'DELETE',
    })
    return response.success
  },

  async searchMemories(query: string, topK: number = 5): Promise<MemorySearchResult[]> {
    return fetchJson<MemorySearchResult[]>(`${API_BASE}/search?query=${encodeURIComponent(query)}&top_k=${topK}`, {
      method: 'POST',
    })
  },

  async getMemoryStats(): Promise<MemoryStats> {
    return fetchJson<MemoryStats>(`${API_BASE}/stats`)
  },

  async clearAllMemories(): Promise<boolean> {
    const response = await fetchJson<{ success: boolean }>(`${API_BASE}/clear`, {
      method: 'DELETE',
    })
    return response.success
  },

  async clearCoreMemory(): Promise<boolean> {
    const response = await fetchJson<{ success: boolean }>(`${API_BASE}/clear/core`, {
      method: 'DELETE',
    })
    return response.success
  },

  async clearRecallMemories(): Promise<boolean> {
    const response = await fetchJson<{ success: boolean }>(`${API_BASE}/clear/recall`, {
      method: 'DELETE',
    })
    return response.success
  },

  async clearArchivalMemories(): Promise<boolean> {
    const response = await fetchJson<{ success: boolean }>(`${API_BASE}/clear/archival`, {
      method: 'DELETE',
    })
    return response.success
  },

  async getMemoryContext(query: string): Promise<string> {
    const response = await fetchJson<{ context: string }>(`${API_BASE}/context?query=${encodeURIComponent(query)}`)
    return response.context
  },

  async getUserProfile(): Promise<string> {
    const response = await fetchJson<{ profile: string }>(`${API_BASE}/profile`)
    return response.profile
  },

  async getRecommendedSkills(): Promise<string[]> {
    const response = await fetchJson<{ skills: string[] }>(`${API_BASE}/recommended-skills`)
    return response.skills
  },

  async processConversation(data: ProcessConversationRequest): Promise<MemoryExtractionResult> {
    return fetchJson<MemoryExtractionResult>(`${API_BASE}/process-conversation`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async getMemoryConfig(): Promise<MemoryConfig> {
    return fetchJson<MemoryConfig>(`${API_BASE}/config`)
  },

  async updateMemoryConfig(config: Partial<MemoryConfig>): Promise<MemoryConfig> {
    return fetchJson<MemoryConfig>(`${API_BASE}/config`, {
      method: 'PUT',
      body: JSON.stringify(config),
    })
  },

  async storeMemory(
    text: string,
    category?: MemoryCategory,
    importance?: number
  ): Promise<RecallMemory> {
    return fetchJson<RecallMemory>(`${API_BASE}/store`, {
      method: 'POST',
      body: JSON.stringify({ text, category, importance }),
    })
  },

  async recallMemories(query: string, limit?: number): Promise<MemorySearchResult[]> {
    return fetchJson<MemorySearchResult[]>(
      `${API_BASE}/recall-search?query=${encodeURIComponent(query)}&limit=${limit || 5}`
    )
  },

  async forgetMemory(memoryId?: string): Promise<boolean> {
    const url = memoryId ? `${API_BASE}/forget/${memoryId}` : `${API_BASE}/forget`
    const response = await fetchJson<{ success: boolean }>(url, {
      method: 'DELETE',
    })
    return response.success
  },

  async getMemoryContextResult(query: string): Promise<MemoryContextResult> {
    return fetchJson<MemoryContextResult>(
      `${API_BASE}/context-result?query=${encodeURIComponent(query)}`
    )
  },

  async cleanupExpiredMemories(): Promise<{ deleted: number }> {
    return fetchJson<{ deleted: number }>(`${API_BASE}/cleanup`, {
      method: 'POST',
    })
  },
}
