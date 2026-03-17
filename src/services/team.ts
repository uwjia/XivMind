import type {
  TeamResult,
  TeamExecuteRequest,
  TaskAnalysisResult,
  SessionSummary,
  TeamStats,
} from '@/types/team'
import { API_BASE_URL } from './config'

const API_BASE = `${API_BASE_URL}/api/team`

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
  return response.json()
}

export const teamService = {
  async analyzeTask(request: TeamExecuteRequest): Promise<TaskAnalysisResult> {
    return fetchJson<TaskAnalysisResult>(`${API_BASE}/analyze`, {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  async executeTask(request: TeamExecuteRequest): Promise<TeamResult> {
    return fetchJson<TeamResult>(`${API_BASE}/execute`, {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  async getSessions(): Promise<{ sessions: string[] }> {
    return fetchJson<{ sessions: string[] }>(`${API_BASE}/sessions`)
  },

  async getSession(sessionId: string): Promise<Record<string, any>> {
    return fetchJson<Record<string, any>>(`${API_BASE}/sessions/${sessionId}`)
  },

  async getSessionSummary(sessionId: string): Promise<SessionSummary> {
    return fetchJson<SessionSummary>(`${API_BASE}/sessions/${sessionId}/summary`)
  },

  async cancelSession(sessionId: string): Promise<void> {
    await fetchJson<void>(`${API_BASE}/sessions/${sessionId}/cancel`, {
      method: 'POST',
    })
  },

  async getStats(): Promise<TeamStats> {
    return fetchJson<TeamStats>(`${API_BASE}/stats`)
  },
}
