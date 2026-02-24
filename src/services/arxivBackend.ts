const BACKEND_API_BASE = '/api/arxiv'

interface Paper {
  id: string
  arxivId: string
  title: string
  abstract: string
  authors: string[]
  category: string
  primaryCategory: string
  categoryId: string
  categories: string[]
  published: Date
  updated: Date
  date: Date
  pdfUrl: string
  absUrl: string
  comment?: string
  journalRef?: string
  doi?: string
  citations: number
  downloads: number
}

interface BackendPaper {
  id: string
  title: string
  abstract: string
  authors: string[]
  primary_category: string
  categories: string[]
  published: string
  updated: string
  pdf_url: string
  abs_url: string
  comment: string
  journal_ref: string
  doi: string
  similarity_score?: number
}

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

function transformBackendPaper(bp: BackendPaper): Paper {
  const primaryCategory = bp.primary_category || ''
  const categoryId = primaryCategory.split('.')[0] || 'cs'
  
  return {
    id: bp.id,
    arxivId: bp.id,
    title: bp.title || '',
    abstract: bp.abstract || '',
    authors: bp.authors || [],
    category: primaryCategory,
    primaryCategory: primaryCategory,
    categoryId: categoryId,
    categories: bp.categories || [],
    published: new Date(bp.published),
    updated: new Date(bp.updated),
    date: new Date(bp.published),
    pdfUrl: bp.pdf_url || '',
    absUrl: bp.abs_url || '',
    comment: bp.comment || '',
    journalRef: bp.journal_ref || '',
    doi: bp.doi || '',
    citations: Math.floor(Math.random() * 100),
    downloads: Math.floor(Math.random() * 500)
  }
}

interface FetchOptions {
  category?: string
  maxResults?: number
  start?: number
}

export const arxivBackendAPI = {
  async fetchPapers(options: FetchOptions = {}): Promise<Paper[]> {
    const {
      category,
      maxResults = 50,
      start = 0
    } = options

    const today = new Date()
    const dateStr = today.toISOString().split('T')[0]
    
    return this.queryPapers(dateStr, category, maxResults, start)
  },

  async queryPapers(
    date: string,
    category?: string,
    maxResults?: number,
    start: number = 0,
    fetchCategory: string = 'cs*'
  ): Promise<Paper[]> {
    const params = new URLSearchParams({
      date: date,
      start: start.toString(),
      max_results: (maxResults || 50).toString(),
      fetch_category: fetchCategory
    })
    
    if (category && category !== 'all' && category !== 'cs*') {
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
    
    return data.papers.map(transformBackendPaper)
  },

  async fetchTodayPapers(category: string = 'all', maxResults?: number, fetchCategory: string = 'cs*'): Promise<Paper[]> {
    const today = new Date()
    const dateStr = today.toISOString().split('T')[0]
    
    return this.queryPapers(dateStr, category, maxResults, 0, fetchCategory)
  },

  async fetchPapersByDate(category: string = 'all', daysAgo: number = 1, maxResults?: number, fetchCategory: string = 'cs*'): Promise<Paper[]> {
    const targetDate = new Date()
    targetDate.setDate(targetDate.getDate() - daysAgo)
    const dateStr = targetDate.toISOString().split('T')[0]
    
    return this.queryPapers(dateStr, category, maxResults, 0, fetchCategory)
  },

  async fetchPapersByDateRange(
    startDateStr: string, 
    endDateStr: string, 
    category: string = 'cs*', 
    maxResults?: number, 
    start: number = 0
  ): Promise<Paper[]> {
    if (!startDateStr || !endDateStr) {
      throw new Error('startDateStr and endDateStr are required')
    }
    
    console.log('=== fetchPapersByDateRange (Backend) ===')
    console.log('startDateStr:', startDateStr)
    console.log('endDateStr:', endDateStr)
    console.log('category:', category)

    const dateStr = startDateStr.substring(0, 10)
    return this.queryPapers(dateStr, category, maxResults, start)
  },

  async searchPapers(_query: string, category: string = 'cs*', maxResults?: number): Promise<Paper[]> {
    console.log('searchPapers: Using backend with today date')
    const today = new Date()
    const dateStr = today.toISOString().split('T')[0]
    
    return this.queryPapers(dateStr, category, maxResults)
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
        papers.push(transformBackendPaper(data))
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
    return transformBackendPaper(data)
  },

  async getDateIndexes(): Promise<DateIndex[]> {
    const response = await fetch(`${BACKEND_API_BASE}/date-indexes`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    return data.indexes || []
  },

  async getStatistics(): Promise<Statistics> {
    const response = await fetch(`${BACKEND_API_BASE}/statistics`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },

  async fetchPapersForDate(date: string, category: string = 'cs*'): Promise<{ success: boolean; date: string; count: number; error?: string }> {
    const params = new URLSearchParams({ category })
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
    const response = await fetch(`${BACKEND_API_BASE}/search`, {
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

  async getEmbeddingIndexes(): Promise<{ indexes: EmbeddingIndex[] }> {
    const response = await fetch(`${BACKEND_API_BASE}/embedding-indexes`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  }
}

export type { Paper, BackendPaper, DateIndex, EmbeddingIndex, Statistics }
