import { API_BASE_URL } from './config'
import type { Paper, BackendPaper } from '@/types'
import { TransformBackendPaper } from '@/types'

const BACKEND_API_BASE = `${API_BASE_URL}/api/arxiv`


interface DateIndex {
  date: string
  total_count: number
  fetched_at: string
}

interface EmbeddingIndex {
  date: string
  total_count: number
  generated_at: string
  model_name?: string
}

interface Statistics {
  total_days: number
  total_papers: number
  indexes: DateIndex[]
}

interface QueryResponse {
  papers: BackendPaper[]
  total: number
  start: number
  max_results: number
}

interface QueryResult {
  papers: Paper[]
  total: number
}


interface FetchOptions {
  category?: string
  maxResults?: number
  start?: number
  subject?: string
}

export const arxivBackendAPI = {
  async fetchTodayPapers(options: FetchOptions = {}): Promise<QueryResult> {
    const {
      category,
      maxResults = 50,
      start = 0,
      subject = 'cs'
    } = options as FetchOptions & { subject?: string }

    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    const dateStr = yesterday.toISOString().split('T')[0]

    return this.queryPapers(dateStr, category, maxResults, start, subject)
  },

  async queryPapers(
    date: string,
    category?: string,
    maxResults?: number,
    start: number = 0,
    subject: string = 'cs'
  ): Promise<QueryResult> {
    const params = new URLSearchParams({
      date: date,
      start: start.toString(),
      max_results: (maxResults || 50).toString(),
      subject: subject
    })

    if (category && category !== 'all' && category !== `${subject}*`) {
      params.append('category', category)
    }

    const url = `${BACKEND_API_BASE}/query?${params}`
    console.log('Backend API URL:', url)

    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data: QueryResponse = await response.json()
    console.log('Backend response:', data.papers.length, 'papers, total:', data.total)

    return {
      papers: data.papers.map(TransformBackendPaper),
      total: data.total
    }
  },

  async fetchPapersByDate(category: string = 'all', daysAgo: number = 1, maxResults?: number, subject: string = 'cs'): Promise<QueryResult> {
    const targetDate = new Date()
    targetDate.setDate(targetDate.getDate() - daysAgo)
    const dateStr = targetDate.toISOString().split('T')[0]

    return this.queryPapers(dateStr, category, maxResults, 0, subject)
  },

  async fetchPapersByDateRange(
    startDateStr: string,
    endDateStr: string,
    category: string = 'cs*',
    maxResults?: number,
    start: number = 0,
    subject: string = 'cs'
  ): Promise<QueryResult> {
    if (!startDateStr || !endDateStr) {
      throw new Error('startDateStr and endDateStr are required')
    }
    const dateStr = startDateStr.substring(0, 10)
    return this.queryPapers(dateStr, category, maxResults, start, subject)
  },

  async searchPapersByKeyword(
    query: string, 
    category: string = 'cs*', 
    maxResults?: number,
    dateFrom?: string,
    dateTo?: string,
    titleOnly?: boolean,
    exactPhrase?: boolean
  ): Promise<QueryResult> {
    const params = new URLSearchParams({
      q: query,
      category: category,
      max_results: (maxResults || 50).toString()
    })
    
    if (dateFrom) {
      params.append('date_from', dateFrom)
    }
    if (dateTo) {
      params.append('date_to', dateTo)
    }
    if (titleOnly) {
      params.append('title_only', 'true')
    }
    if (exactPhrase) {
      params.append('exact_phrase', 'true')
    }
    
    const url = `${BACKEND_API_BASE}/search_k?${params}`
    console.log('Backend search URL:', url)
    
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data: QueryResponse = await response.json()
    console.log('Backend search response:', data.papers.length, 'papers, total:', data.total)
    
    return {
      papers: data.papers.map(TransformBackendPaper),
      total: data.total
    }
  },

  async fetchPapersByIdList(idList: string | string[]): Promise<Paper[]> {
    if (!idList || (Array.isArray(idList) && idList.length === 0)) {
      throw new Error('idList is required')
    }

    const ids = Array.isArray(idList) ? idList : [idList]
    console.log('=== fetchPapersByIdList (Backend) ===')
    console.log('IDs:', ids)

    const papers: Paper[] = []
    for (const id of ids) {
      const response = await fetch(`${BACKEND_API_BASE}/paper/${id}`)
      if (response.ok) {
        const data: BackendPaper = await response.json()
        papers.push(TransformBackendPaper(data))
      }
    }

    console.log('Fetched papers:', papers.length)
    return papers
  },

  async getPaperById(paperId: string): Promise<Paper | null> {
    const response = await fetch(`${BACKEND_API_BASE}/paper/${paperId}`)
    if (!response.ok) {
      return null
    }
    const data: BackendPaper = await response.json()
    return TransformBackendPaper(data)
  },

  async getDateIndexes(subject: string = 'cs'): Promise<DateIndex[]> {
    const params = new URLSearchParams({ subject })
    const response = await fetch(`${BACKEND_API_BASE}/date-indexes?${params}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    return data.indexes || []
  },

  async getStatistics(subject: string = 'cs'): Promise<Statistics> {
    const params = new URLSearchParams({ subject })
    const response = await fetch(`${BACKEND_API_BASE}/statistics?${params}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },

  async fetchPapersForDate(date: string, subject: string = 'cs'): Promise<{ success: boolean; date: string; subject?: string; count: number; error?: string }> {
    const params = new URLSearchParams({ subject })
    const response = await fetch(`${BACKEND_API_BASE}/fetch/${date}?${params}`, { method: 'POST' })
    return response.json()
  },

  async clearDateCache(date: string): Promise<void> {
    const response = await fetch(`${BACKEND_API_BASE}/cache/date/${date}`, { method: 'DELETE' })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
  },

  async clearAllDateCache(): Promise<void> {
    const response = await fetch(`${BACKEND_API_BASE}/cache/date`, { method: 'DELETE' })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
  },

  async generateEmbeddings(options: {
    date?: string
    dateFrom?: string
    dateTo?: string
    force?: boolean
    batchSize?: number
  } = {}): Promise<{
    success: boolean
    generated_count: number
    skipped_count: number
    error_count: number
    error?: string
  }> {
    const response = await fetch(`${BACKEND_API_BASE}/embeddings/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        date: options.date,
        date_from: options.dateFrom,
        date_to: options.dateTo,
        force: options.force || false,
        batch_size: options.batchSize || 100
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async semanticSearch(query: string, topK: number = 10): Promise<{
    papers: BackendPaper[]
    total: number
    query: string
    model?: string
    error?: string
  }> {
    const response = await fetch(`${BACKEND_API_BASE}/search_s`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query,
        top_k: topK
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async askQuestion(question: string, topK: number = 5, provider?: string, model?: string): Promise<{
    answer: string
    references: Array<{
      id: string
      title: string
      authors: string[]
      published?: string
      relevance_score: number
    }>
    model?: string
    error?: string
  }> {
    const body: Record<string, any> = {
      question,
      top_k: topK,
      include_references: true
    }
    
    if (provider) {
      body.provider = provider
    }
    if (model) {
      body.model = model
    }
    
    const response = await fetch(`${BACKEND_API_BASE}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async askQuestionWithMemory(
    question: string, 
    topK: number = 5, 
    useMemory: boolean = true,
    provider?: string, 
    model?: string
  ): Promise<{
    answer: string
    references: Array<{
      id: string
      title: string
      authors: string[]
      published?: string
      relevance_score: number
    }>
    model?: string
    memory_used: boolean
    relevant_memories_count: number
    error?: string
  }> {
    const body: Record<string, any> = {
      question,
      top_k: topK,
      include_references: true,
      use_memory: useMemory,
      user_id: 'default'
    }
    
    if (provider) {
      body.provider = provider
    }
    if (model) {
      body.model = model
    }
    
    const response = await fetch(`${BACKEND_API_BASE}/ask-with-memory`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async getEmbeddingIndexes(): Promise<{ indexes: EmbeddingIndex[] }> {
    const response = await fetch(`${BACKEND_API_BASE}/embedding-indexes`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },

  async fetchPapersByAuthor(
    authorName: string,
    maxResults: number = 50,
    start: number = 0,
    subject: string = 'cs'
  ): Promise<QueryResult> {
    const encodedAuthor = encodeURIComponent(authorName)
    const params = new URLSearchParams({
      start: start.toString(),
      max_results: maxResults.toString(),
      subject: subject
    })

    const url = `${BACKEND_API_BASE}/author/${encodedAuthor}?${params}`
    console.log('Fetching papers by author:', url)

    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    return {
      papers: (data.papers || []).map(TransformBackendPaper),
      total: data.total || 0
    }
  }
}

export type { Paper, BackendPaper, DateIndex, EmbeddingIndex, Statistics }
