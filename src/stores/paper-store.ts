import { defineStore } from 'pinia'
import { ref } from 'vue'
import { arxivAPI } from '@/services/arxiv'
import { arxivBackendAPI } from '@/services/arxivBackend'
import { useConfigStore } from '@/stores/config-store'
import type { Paper } from '@/types'

interface FetchOptions {
  category?: string
  maxResults?: number
  start?: number
}

export const usePaperStore = defineStore('paper', () => {
  const papers = ref<Paper[]>([])
  const searchQuery = ref<string>('')
  const selectedCategory = ref<string>('all')
  const selectedDate = ref<string | Date | { startDate: string; endDate: string }>('all')
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const currentPage = ref<number>(0)
  const totalPapers = ref<number>(0)

  const setPapers = (data: Paper[]) => {
    papers.value = data
  }

  const setTotalPapers = (total: number) => {
    totalPapers.value = total
  }

  const addOrUpdatePaper = (paper: Paper) => {
    const existingIndex = papers.value.findIndex((p: Paper) => p.id === paper.id)
    if (existingIndex >= 0) {
      papers.value[existingIndex] = paper
    } else {
      papers.value.push(paper)
    }
  }

  const addOrUpdatePapers = (newPapers: Paper[]) => {
    newPapers.forEach(newPaper => {
      addOrUpdatePaper(newPaper)
    })
  }

  const setSearchQuery = (query: string) => {
    searchQuery.value = query
  }

  const setSelectedCategory = (category: string) => {
    selectedCategory.value = category
  }

  const setSelectedDate = (date: string | Date | { startDate: string; endDate: string }) => {
    selectedDate.value = date
  }

  const setCurrentPage = (page: number) => {
    currentPage.value = page
  }

  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const setError = (value: string | null) => {
    error.value = value
  }

  const fetchTodayPapersBackend = async (options: FetchOptions = {}) => {
    try {
      setLoading(true)
      setError(null)

      const configStore = useConfigStore()
      const { category, maxResults = configStore.maxResults, start = 0 } = options

      const result = await arxivBackendAPI.fetchTodayPapers({
        category,
        maxResults,
        start,
        subject: configStore.defaultSubject
      })
      setPapers(result.papers)
      setTotalPapers(result.total)

      return result.papers
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Error fetching papers:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchTodayPapers = async (category: string = 'cs', maxResults?: number) => {
    try {
      setLoading(true)
      setError(null)

      const configStore = useConfigStore()
      const actualMaxResults = maxResults || configStore.maxResults
      const data = await arxivAPI.fetchTodayPapers(category, actualMaxResults)
      setPapers(data)

      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Error fetching today papers:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchPapersByDateRange = async (startDateStr: string, endDateStr: string, category?: string, maxResults?: number, start: number = 0) => {
    try {
      setLoading(true)
      setError(null)

      console.log('=== fetchPapersByDateRange ===')
      console.log('startDateStr:', startDateStr)
      console.log('endDateStr:', endDateStr)

      const configStore = useConfigStore()
      const actualMaxResults = maxResults || configStore.maxResults
      const actualCategory = category || `${configStore.defaultSubject}*`
      const result = await arxivBackendAPI.fetchPapersByDateRange(
        startDateStr,
        endDateStr,
        actualCategory,
        actualMaxResults,
        start,
        configStore.defaultSubject
      )
      setPapers(result.papers)
      setTotalPapers(result.total)

      console.log('Papers fetched after date range selection:', result.papers.length)
      return result.papers
    } catch (err) {
      console.error('Error fetching papers after date range selection:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const searchPapers = async (query: string, category: string = 'cs*', maxResults?: number) => {
    try {
      setLoading(true)
      setError(null)

      const configStore = useConfigStore()
      const actualMaxResults = maxResults || configStore.maxResults
      const data = await arxivAPI.searchPapers(query, category, actualMaxResults)
      setPapers(data)

      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Error searching papers:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getPaperById = (id: string): Paper | undefined => {
    return papers.value.find(paper => paper.id === id)
  }

  const fetchPaperById = async (id: string) => {
    try {
      setLoading(true)
      setError(null)

      const data = await arxivBackendAPI.getPaperById(id)
      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Error fetching papers by IDs:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getFilteredPapers = (): Paper[] => {
    return papers.value
  }

  return {
    papers,
    searchQuery,
    selectedCategory,
    selectedDate,
    loading,
    error,
    currentPage,
    totalPapers,
    setPapers,
    setTotalPapers,
    addOrUpdatePaper,
    addOrUpdatePapers,
    setSearchQuery,
    setSelectedCategory,
    setSelectedDate,
    setCurrentPage,
    setLoading,
    setError,
    fetchTodayPapersBackend,
    fetchTodayPapers,
    fetchPapersByDateRange,
    searchPapers,
    fetchPaperById,
    getPaperById,
    getFilteredPapers
  }
})
