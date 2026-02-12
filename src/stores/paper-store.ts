import { defineStore } from 'pinia'
import { ref } from 'vue'
import { arxivAPI } from '../services/arxiv'
import { useConfigStore } from './config-store'
import type { Paper } from '../types'

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

  const setPapers = (data: Paper[]) => {
    papers.value = data
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

  const fetchPapers = async (options: FetchOptions = {}) => {
    try {
      setLoading(true)
      setError(null)

      const configStore = useConfigStore()
      const { category = 'cs*', maxResults = configStore.maxResults, start = 0 } = options

      const data = await arxivAPI.fetchPapers({ category, maxResults, start })
      setPapers(data)

      return data
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

  const fetchPapersByDateRange = async (startDateStr: string, endDateStr: string, category: string = 'cs*', maxResults?: number, start: number = 0) => {
    try {
      setLoading(true)
      setError(null)

      console.log('=== fetchPapersByDateRange ===')
      console.log('startDateStr:', startDateStr)
      console.log('endDateStr:', endDateStr)

      const configStore = useConfigStore()
      const actualMaxResults = maxResults || configStore.maxResults
      const data = await arxivAPI.fetchPapersByDateRange(startDateStr, endDateStr, category, actualMaxResults, start)
      setPapers(data)

      console.log('Papers fetched after date range selection:', data.length)
      return data
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

  const fetchPapersByIds = async (idList: string[]) => {
    try {
      setLoading(true)
      setError(null)

      const data = await arxivAPI.fetchPapersByIdList(idList)
      // addOrUpdatePapers(data)

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
    setPapers,
    addOrUpdatePaper,
    addOrUpdatePapers,
    setSearchQuery,
    setSelectedCategory,
    setSelectedDate,
    setCurrentPage,
    setLoading,
    setError,
    fetchPapers,
    fetchTodayPapers,
    fetchPapersByDateRange,
    searchPapers,
    fetchPapersByIds,
    getPaperById,
    getFilteredPapers
  }
})
