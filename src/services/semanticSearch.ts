import { API_BASE_URL } from './config'
import type { SemanticSearchPaper } from '@/types/dailyAnalysis'

const API_BASE = `${API_BASE_URL}/api/arxiv`

export interface SearchOptions {
  topK?: number
  category?: string
  dateFrom?: string
  dateTo?: string
}

export interface SearchResponse {
  papers: SemanticSearchPaper[]
  total: number
  query: string
  model?: string
  error?: string
}

export const semanticSearchAPI = {
  async searchPapers(query: string, options: SearchOptions = {}): Promise<SearchResponse> {
    const topK = options.topK ?? 50

    const response = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        top_k: topK,
        category: options.category,
        date_from: options.dateFrom,
        date_to: options.dateTo,
      }),
    })

    if (!response.ok) {
      throw new Error(`Search failed: ${response.statusText}`)
    }

    return response.json()
  },
}
