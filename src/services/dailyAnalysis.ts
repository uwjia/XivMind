import { API_BASE_URL } from './config'
import type { AnalysisMode, AnalysisLanguage } from '@/types/dailyAnalysis'

const API_BASE = `${API_BASE_URL}/api/daily-analysis`

export interface StreamAnalysisOptions {
  date: string
  mode: AnalysisMode
  userInterests?: string[]
  provider?: string
  model?: string
  language: AnalysisLanguage
  maxPapers: number
}

export interface StreamEvent {
  type: string
  content: Record<string, unknown>
}

export interface PaperCountResponse {
  total_papers: number
}

export const dailyAnalysisAPI = {
  async fetchPaperCount(date: string): Promise<PaperCountResponse> {
    const response = await fetch(`${API_BASE}/papers/count/${date}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch paper count: ${response.statusText}`)
    }
    return response.json()
  },

  async *streamAnalysis(
    options: StreamAnalysisOptions,
    signal?: AbortSignal
  ): AsyncGenerator<StreamEvent, void, unknown> {
    const response = await fetch(`${API_BASE}/analyze/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        date: options.date,
        mode: options.mode,
        user_interests: options.userInterests,
        provider: options.provider || undefined,
        model: options.model || undefined,
        language: options.language,
        max_papers: options.maxPapers,
      }),
      signal,
    })

    if (!response.ok) {
      throw new Error(`Analysis failed: ${response.statusText}`)
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const event = JSON.parse(line.slice(6))
            yield event as StreamEvent
          } catch (parseError) {
            console.warn('Failed to parse event:', line)
          }
        }
      }
    }
  },
}
