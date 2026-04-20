import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { arxivAPI } from '@/services/arxiv'
import { arxivBackendAPI } from '@/services/arxivBackend'
import { semanticSearchAPI } from '@/services/semanticSearch'
import type { Paper } from '@/types'
import type { SemanticSearchPaper } from '@/types/dailyAnalysis'

export type SearchSource = 'arxiv' | 'backend' | 'semantic'
export type BackendSearchType = 'keyword' | 'author'

const PAPER_ID_PATTERN = /^\d{4}\.\d{4,5}?(v\d+)?$/

export interface SearchParams {
  query: string
  source: SearchSource
  searchType?: BackendSearchType
  category?: string
  maxResults?: number
  topK?: number
  dateFrom?: string
  dateTo?: string
  titleOnly?: boolean
  exactPhrase?: boolean
}

function convertSemanticPaperToPaper(semanticPaper: SemanticSearchPaper): Paper {
  return {
    id: semanticPaper.id,
    arxivId: semanticPaper.id,
    title: semanticPaper.title,
    abstract: semanticPaper.abstract || '',
    authors: semanticPaper.authors || [],
    category: semanticPaper.primary_category || '',
    primaryCategory: semanticPaper.primary_category || '',
    categoryId: semanticPaper.primary_category?.split('.')[0] || 'cs',
    categories: semanticPaper.categories || [],
    published: new Date(semanticPaper.published || Date.now()),
    updated: new Date(semanticPaper.published || Date.now()),
    date: new Date(semanticPaper.published || Date.now()),
    pdfUrl: semanticPaper.pdf_url || '',
    absUrl: semanticPaper.abs_url || `https://arxiv.org/abs/${semanticPaper.id}`,
    citations: 0,
    downloads: 0
  }
}

export function useSearch() {
  const route = useRoute()
  
  const papers = ref<Paper[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')
  const searchSource = ref<SearchSource>('backend')
  const sortBy = ref('date')
  const totalResults = ref(0)
  
  const currentPage = ref(1)
  const pageInput = ref(1)
  const pageSize = ref(50)
  const pageSizeOptions = [50, 100, 200, 500, 1000, 2000]

  const sortedPapers = computed(() => {
    const papersCopy = [...papers.value]
    switch (sortBy.value) {
      case 'date':
        return papersCopy.sort((a, b) => {
          const dateA = a.date ? new Date(a.date).getTime() : 0
          const dateB = b.date ? new Date(b.date).getTime() : 0
          return dateB - dateA
        })
      case 'citations':
        return papersCopy.sort((a, b) => (b.citations || 0) - (a.citations || 0))
      case 'views':
        return papersCopy.sort((a, b) => (b.downloads || 0) - (a.downloads || 0))
      default:
        return papersCopy
    }
  })

  const totalPages = computed(() => {
    return Math.ceil(sortedPapers.value.length / pageSize.value)
  })

  const currentPapers = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return sortedPapers.value.slice(start, end)
  })

  const visiblePages = computed(() => {
    const pages: (number | string)[] = []
    const total = totalPages.value
    const current = currentPage.value

    if (total <= 7) {
      for (let i = 1; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      if (current > 3) {
        pages.push('...')
      }
      const start = Math.max(2, current - 1)
      const end = Math.min(total - 1, current + 1)
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      if (current < total - 2) {
        pages.push('...')
      }
      pages.push(total)
    }

    return pages
  })

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
      pageInput.value = page
      window.scrollTo({ top: 0, behavior: 'instant' })
    }
  }

  const jumpToPage = () => {
    const page = pageInput.value
    if (page >= 1 && page <= totalPages.value) {
      goToPage(page)
    } else {
      pageInput.value = currentPage.value
    }
  }

  const changePageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    pageInput.value = 1
    window.scrollTo({ top: 0, behavior: 'instant' })
  }

  const searchWithArxiv = async (params: SearchParams) => {
    const result = await arxivAPI.searchPapers(
      params.query,
      params.category || 'cs*',
      params.maxResults || 50
    )
    return { papers: result, total: result.length }
  }

  const searchWithBackend = async (params: SearchParams) => {
    const searchType = params.searchType || 'keyword'
    
    if (searchType === 'author') {
      const result = await arxivBackendAPI.fetchPapersByAuthor(
        params.query,
        params.maxResults || 50
      )
      return { papers: result.papers, total: result.total }
    }
    
    if (PAPER_ID_PATTERN.test(params.query.trim())) {
      let paperId = params.query.trim()
      const versionMatch = paperId.match(/^(.+?)v\d+$/)
      if (versionMatch) {
        paperId = versionMatch[1]
      }
      const paper = await arxivBackendAPI.getPaperById(paperId)
      if (paper) {
        return { papers: [paper], total: 1 }
      }
      return { papers: [], total: 0 }
    }
    
    const result = await arxivBackendAPI.searchPapersByKeyword(
      params.query,
      params.category || 'cs*',
      params.maxResults || 50,
      params.dateFrom,
      params.dateTo,
      params.titleOnly,
      params.exactPhrase
    )
    return { papers: result.papers, total: result.total }
  }

  const searchWithSemantic = async (params: SearchParams) => {
    const result = await semanticSearchAPI.searchPapers(params.query, {
      topK: params.topK || 50,
      category: params.category,
      dateFrom: params.dateFrom,
      dateTo: params.dateTo
    })
    const convertedPapers = result.papers.map(convertSemanticPaperToPaper)
    return { papers: convertedPapers, total: result.total }
  }

  const performSearch = async (params: SearchParams) => {
    if (!params.query.trim()) {
      papers.value = []
      totalResults.value = 0
      return
    }

    isLoading.value = true
    error.value = null

    try {
      let result: { papers: Paper[], total: number }

      switch (params.source) {
        case 'arxiv':
          result = await searchWithArxiv(params)
          break
        case 'backend':
          result = await searchWithBackend(params)
          break
        case 'semantic':
          result = await searchWithSemantic(params)
          break
        default:
          result = await searchWithBackend(params)
      }

      papers.value = result.papers
      totalResults.value = result.total
      searchQuery.value = params.query
      searchSource.value = params.source
      currentPage.value = 1
      pageInput.value = 1
    } catch (err) {
      console.error('Search failed:', err)
      error.value = err instanceof Error ? err.message : 'Search failed'
      papers.value = []
      totalResults.value = 0
    } finally {
      isLoading.value = false
    }
  }

  const parseQueryParams = (): SearchParams | null => {
    const q = route.query.q as string
    if (!q) return null

    const source = (route.query.source as SearchSource) || 'backend'
    const searchType = (route.query.searchType as BackendSearchType) || 'keyword'
    
    return {
      query: q,
      source,
      searchType,
      category: route.query.category as string | undefined,
      maxResults: route.query.maxResults ? Number(route.query.maxResults) : undefined,
      topK: route.query.topK ? Number(route.query.topK) : undefined,
      dateFrom: route.query.dateFrom as string | undefined,
      dateTo: route.query.dateTo as string | undefined,
      titleOnly: route.query.titleOnly === 'true',
      exactPhrase: route.query.exactPhrase === 'true'
    }
  }

  const handleRouteChange = async () => {
    const params = parseQueryParams()
    if (params) {
      await performSearch(params)
    }
  }

  watch(
    () => route.query,
    () => {
      handleRouteChange()
    },
    { immediate: true }
  )

  return {
    papers,
    sortedPapers,
    currentPapers,
    isLoading,
    error,
    searchQuery,
    searchSource,
    sortBy,
    totalResults,
    currentPage,
    pageInput,
    pageSize,
    pageSizeOptions,
    totalPages,
    visiblePages,
    goToPage,
    jumpToPage,
    changePageSize,
    performSearch,
    handleRouteChange
  }
}
