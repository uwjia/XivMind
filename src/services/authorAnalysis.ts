import type { AuthorRank, AnalysisStatus, AuthorAnalysisStatistics, AuthorMetricType } from '@/types/authorAnalysis'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  })
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  return response.json()
}

export interface TopAuthorsResponse {
  authors: AuthorRank[]
  total: number
  limit: number
  offset: number
}

export const authorAnalysisAPI = {
  getTopAuthors: async (
    metric: AuthorMetricType = 'pagerank',
    category?: string,
    nameSearch?: string,
    limit: number = 100,
    offset: number = 0,
  ): Promise<TopAuthorsResponse> => {
    const params = new URLSearchParams({
      metric,
      limit: limit.toString(),
      offset: offset.toString(),
    })
    if (category) {
      params.append('category', category)
    }
    if (nameSearch) {
      params.append('name_search', nameSearch)
    }
    
    return request<TopAuthorsResponse>(`/api/author-analysis/top-authors?${params}`)
  },

  getAuthorDetail: async (authorId: string): Promise<AuthorRank> => {
    return request<AuthorRank>(`/api/author-analysis/author/${encodeURIComponent(authorId)}`)
  },

  rebuildAnalysis: async (
    minPapers: number = 3,
    alpha: number = 0.85,
    useDisambiguation: boolean = true,
    similarityThreshold: number = 0.1,
  ): Promise<{ status: string; message: string; progress?: number; total?: number; disambiguation_enabled?: boolean }> => {
    const params = new URLSearchParams({
      min_papers: minPapers.toString(),
      alpha: alpha.toString(),
      use_disambiguation: useDisambiguation.toString(),
      similarity_threshold: similarityThreshold.toString(),
    })
    return request(`/api/author-analysis/rebuild?${params}`, {
      method: 'POST',
    })
  },

  getAnalysisStatus: async (): Promise<AnalysisStatus> => {
    return request<AnalysisStatus>('/api/author-analysis/status')
  },

  getStatistics: async (): Promise<AuthorAnalysisStatistics> => {
    return request<AuthorAnalysisStatistics>('/api/author-analysis/statistics')
  },

  clearAnalysisData: async (): Promise<{ status: string; message: string }> => {
    return request('/api/author-analysis/clear', {
      method: 'DELETE',
    })
  },
}
