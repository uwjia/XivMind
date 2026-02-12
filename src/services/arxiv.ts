const ARXIV_API_BASE = '/api/arxiv/api/query'

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
  citations: number
  downloads: number
}

interface FetchOptions {
  category?: string
  maxResults?: number
  sortBy?: string
  sortOrder?: string
  start?: number
}

export const arxivAPI = {
  async fetchPapers(options: FetchOptions = {}): Promise<Paper[]> {
    const {
      category = 'cs*',
      maxResults,
      sortBy = 'submittedDate',
      sortOrder = 'descending',
      start = 0
    } = options

    const searchQuery = `cat:${category}`

    const params = new URLSearchParams({
      search_query: searchQuery,
      start: start.toString(),
      max_results: maxResults?.toString() || '50',
      sortBy,
      sortOrder
    })

    try {
      const response = await fetch(`${ARXIV_API_BASE}?${params}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const text = await response.text()
      console.log('arXiv API response:', text.substring(0, 500))
      
      const parser = new DOMParser()
      const xmlDoc = parser.parseFromString(text, 'text/xml')

      const entries = xmlDoc.querySelectorAll('entry')
      console.log('Found entries:', entries.length)
      
      const papers: Paper[] = []

      entries.forEach((entry, index) => {
        try {
          const id = entry.querySelector('id')?.textContent || ''
          const published = entry.querySelector('published')?.textContent || ''
          const updated = entry.querySelector('updated')?.textContent || ''
          const title = entry.querySelector('title')?.textContent || ''
          const summary = entry.querySelector('summary')?.textContent || ''
          
          const authors: string[] = []
          entry.querySelectorAll('author name').forEach(name => {
            authors.push(name.textContent || '')
          })

          const categories: string[] = []
          entry.querySelectorAll('category').forEach(cat => {
            categories.push(cat.getAttribute('term') || '')
          })

          const commentElement = Array.from(entry.querySelectorAll('*')).find(el => 
            el.tagName.toLowerCase().includes('comment')
          )
          const comment = commentElement?.textContent?.trim() || ''

          const primaryCategory = categories[0] || ''
          const categoryId = primaryCategory.split('.')[0] || 'cs'

          const pdfUrl = entry.querySelector('link[title="pdf"]')?.getAttribute('href') || ''
          const absUrl = id ? `https://arxiv.org/abs/${id.split('/').pop()}` : ''

          if (!id || !title) {
            console.warn(`Skipping entry ${index}: missing id or title`)
            return
          }

          papers.push({
            id: id.split('/').pop() || '',
            arxivId: id.split('/').pop() || '',
            title: title.trim(),
            abstract: summary.trim(),
            authors,
            category: primaryCategory,
            primaryCategory: primaryCategory,
            categoryId: categoryId,
            categories,
            published: new Date(published),
            updated: new Date(updated),
            date: new Date(published),
            pdfUrl,
            absUrl,
            comment: comment.trim(),
            citations: Math.floor(Math.random() * 100),
            downloads: Math.floor(Math.random() * 500)
          })
        } catch (err) {
          console.error(`Error parsing entry ${index}:`, err)
        }
      })

      console.log('Parsed papers:', papers.length)
      return papers
    } catch (error) {
      console.error('Error fetching arXiv papers:', error)
      throw error
    }
  },

  async fetchTodayPapers(category: string = 'all', maxResults?: number): Promise<Paper[]> {
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    const papers = await this.fetchPapers({
      category,
      maxResults,
      sortBy: 'submittedDate',
      sortOrder: 'descending'
    })

    const todayPapers = papers.filter(paper => {
      const paperDate = new Date(paper.published)
      return paperDate >= yesterday
    })

    return todayPapers
  },

  async fetchPapersByDate(category: string = 'all', daysAgo: number = 1, maxResults?: number): Promise<Paper[]> {
    const cutoffDate = new Date()
    cutoffDate.setDate(cutoffDate.getDate() - daysAgo)

    const papers = await this.fetchPapers({
      category,
      maxResults,
      sortBy: 'submittedDate',
      sortOrder: 'descending'
    })

    const filteredPapers = papers.filter(paper => {
      const paperDate = new Date(paper.published)
      return paperDate >= cutoffDate
    })

    return filteredPapers
  },

  async searchPapers(query: string, category: string = 'cs*', maxResults?: number): Promise<Paper[]> {
    const searchQuery = `cat:${category} AND all:${query}`

    const params = new URLSearchParams({
      search_query: searchQuery,
      start: '0',
      max_results: maxResults?.toString() || '50',
      sortBy: 'relevance',
      sortOrder: 'descending'
    })

    try {
      const response = await fetch(`${ARXIV_API_BASE}?${params}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const text = await response.text()
      console.log('arXiv search response:', text.substring(0, 500))
      
      const parser = new DOMParser()
      const xmlDoc = parser.parseFromString(text, 'text/xml')

      const entries = xmlDoc.querySelectorAll('entry')
      console.log('Found search entries:', entries.length)
      
      const papers: Paper[] = []

      entries.forEach((entry, index) => {
        try {
          const id = entry.querySelector('id')?.textContent || ''
          const published = entry.querySelector('published')?.textContent || ''
          const updated = entry.querySelector('updated')?.textContent || ''
          const title = entry.querySelector('title')?.textContent || ''
          const summary = entry.querySelector('summary')?.textContent || ''
          
          const authors: string[] = []
          entry.querySelectorAll('author name').forEach(name => {
            authors.push(name.textContent || '')
          })

          const categories: string[] = []
          entry.querySelectorAll('category').forEach(cat => {
            categories.push(cat.getAttribute('term') || '')
          })

          const commentElement = Array.from(entry.querySelectorAll('*')).find(el => 
            el.tagName.toLowerCase().includes('comment')
          )
          const comment = commentElement?.textContent?.trim() || ''

          const primaryCategory = categories[0] || ''
          const categoryId = primaryCategory.split('.')[0] || 'cs'

          const pdfUrl = entry.querySelector('link[title="pdf"]')?.getAttribute('href') || ''
          const absUrl = id ? `https://arxiv.org/abs/${id.split('/').pop()}` : ''

          if (!id || !title) {
            console.warn(`Skipping search entry ${index}: missing id or title`)
            return
          }

          papers.push({
            id: id.split('/').pop() || '',
            arxivId: id.split('/').pop() || '',
            title: title.trim(),
            abstract: summary.trim(),
            authors,
            category: primaryCategory,
            primaryCategory: primaryCategory,
            categoryId: categoryId,
            categories,
            published: new Date(published),
            updated: new Date(updated),
            date: new Date(published),
            pdfUrl,
            absUrl,
            comment: comment.trim(),
            citations: Math.floor(Math.random() * 100),
            downloads: Math.floor(Math.random() * 500)
          })
        } catch (err) {
          console.error(`Error parsing search entry ${index}:`, err)
        }
      })

      console.log('Parsed search papers:', papers.length)
      return papers
    } catch (error) {
      console.error('Error searching arXiv papers:', error)
      throw error
    }
  },
  async fetchPapersByDateRange(startDateStr: string, endDateStr: string, category: string = 'cs*', maxResults?: number, start: number = 0): Promise<Paper[]> {
    try {
      if (!startDateStr || !endDateStr) {
        throw new Error('startDateStr and endDateStr are required')
      }
      
      console.log('=== fetchPapersByDateRange ===')
      console.log('startDateStr:', startDateStr)
      console.log('endDateStr:', endDateStr)

      const sortBy = 'submittedDate'
      const sortOrder = 'descending'

      const params = new URLSearchParams({
        start: start.toString(),
        max_results: maxResults?.toString() || '50',
        sortBy,
        sortOrder
      })
      
      const searchCat = `cat:${category}`
      const searchDate = `submittedDate:[${startDateStr}+TO+${endDateStr}]`
      const searchQuery = `search_query=${searchDate}+AND+${searchCat}`
      
      const url = `${ARXIV_API_BASE}?${searchQuery}&${params}`
      
      console.log('Final URL:', url)
      
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const text = await response.text()
      console.log('arXiv date range API response:', text.substring(0, 500))
      
      const parser = new DOMParser()
      const xmlDoc = parser.parseFromString(text, 'text/xml')
      const entries = xmlDoc.querySelectorAll('entry')
      console.log('Found entries:', entries.length)
      
      const papers: Paper[] = []
      entries.forEach((entry, index) => {
        try {
            const id = entry.querySelector('id')?.textContent || ''
            const published = entry.querySelector('published')?.textContent || ''
            const updated = entry.querySelector('updated')?.textContent || ''
            const title = entry.querySelector('title')?.textContent || ''
            const summary = entry.querySelector('summary')?.textContent || ''
            
            const authors: string[] = []
            entry.querySelectorAll('author name').forEach(name => {
              authors.push(name.textContent || '')
            })
            
            const categories: string[] = []
            entry.querySelectorAll('category').forEach(cat => {
              categories.push(cat.getAttribute('term') || '')
            })

            const commentElement = Array.from(entry.querySelectorAll('*')).find(el => 
              el.tagName.toLowerCase().includes('comment')
            )
            const comment = commentElement?.textContent?.trim() || ''

            const primaryCategory = categories[0] || ''
            const categoryId = primaryCategory.split('.')[0] || 'cs'
            const pdfUrl = entry.querySelector('link[title="pdf"]')?.getAttribute('href') || ''
            const absUrl = id ? `https://arxiv.org/abs/${id.split('/').pop()}` : ''
            
            if (!id || !title) {
              console.warn(`Skipping entry ${index}: missing id or title`)
              return
            }
            
            papers.push({
              id: id.split('/').pop() || '',
              arxivId: id.split('/').pop() || '',
              title: title.trim(),
              abstract: summary.trim(),
              authors,
              category: primaryCategory,
              primaryCategory: primaryCategory,
              categoryId: categoryId,
              categories,
              published: new Date(published),
              updated: new Date(updated),
              date: new Date(published),
              pdfUrl,
              absUrl,
              comment: comment.trim(),
              citations: Math.floor(Math.random() * 100),
              downloads: Math.floor(Math.random() * 500)
            })
          } catch (err) {
            console.error(`Error parsing entry ${index}:`, err)
          }
        })
      
      console.log('Parsed papers:', papers.length)
      return papers
    } catch (error) {
      console.error('Error fetching arXiv papers by date range:', error)
      throw error
    }
  },

  async fetchPapersByIdList(idList: string | string[]): Promise<Paper[]> {
    try {
      if (!idList || (Array.isArray(idList) && idList.length === 0)) {
        throw new Error('idList is required')
      }

      const ids = Array.isArray(idList) ? idList.join(',') : idList
      const url = `${ARXIV_API_BASE}?id_list=${ids}`

      console.log('=== fetchPapersByIdList ===')
      console.log('URL:', url)

      const response = await fetch(url)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const text = await response.text()
      console.log('arXiv ID list API response:', text.substring(0, 500))

      const parser = new DOMParser()
      const xmlDoc = parser.parseFromString(text, 'text/xml')
      const entries = xmlDoc.querySelectorAll('entry')
      console.log('Found entries:', entries.length)

      const papers: Paper[] = []
      entries.forEach((entry, index) => {
        try {
          const id = entry.querySelector('id')?.textContent || ''
          const published = entry.querySelector('published')?.textContent || ''
          const updated = entry.querySelector('updated')?.textContent || ''
          const title = entry.querySelector('title')?.textContent || ''
          const summary = entry.querySelector('summary')?.textContent || ''

          const authors: string[] = []
          entry.querySelectorAll('author name').forEach(name => {
            authors.push(name.textContent || '')
          })

          const categories: string[] = []
          entry.querySelectorAll('category').forEach(cat => {
            categories.push(cat.getAttribute('term') || '')
          })

          const commentElement = Array.from(entry.querySelectorAll('*')).find(el => 
            el.tagName.toLowerCase().includes('comment')
          )
          const comment = commentElement?.textContent?.trim() || ''

          const primaryCategory = categories[0] || ''
          const categoryId = primaryCategory.split('.')[0] || 'cs'
          const pdfUrl = entry.querySelector('link[title="pdf"]')?.getAttribute('href') || ''
          const absUrl = id ? `https://arxiv.org/abs/${id.split('/').pop()}` : ''

          if (!id || !title) {
            console.warn(`Skipping entry ${index}: missing id or title`)
            return
          }

          papers.push({
            id: id.split('/').pop() || '',
            arxivId: id.split('/').pop() || '',
            title: title.trim(),
            abstract: summary.trim(),
            authors,
            category: primaryCategory,
            primaryCategory: primaryCategory,
            categoryId: categoryId,
            categories,
            published: new Date(published),
            updated: new Date(updated),
            date: new Date(published),
            pdfUrl,
            absUrl,
            comment: comment.trim(),
            citations: Math.floor(Math.random() * 100),
            downloads: Math.floor(Math.random() * 500)
          })
        } catch (err) {
          console.error(`Error parsing entry ${index}:`, err)
        }
      })

      console.log('Parsed papers:', papers.length)
      return papers
    } catch (error) {
      console.error('Error fetching arXiv papers by ID list:', error)
      throw error
    }
  }
}
