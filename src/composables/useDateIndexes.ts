import { ref, computed, type ComputedRef } from 'vue'
import { arxivBackendAPI } from '../services/arxivBackend'

export interface DateIndex {
  date: string
  total_count: number
  fetched_at: string
}

export interface EmbeddingIndex {
  date: string
  total_count: number
  generated_at: string
  model_name?: string
}

export interface DateInfoDetail {
  count: number
  fetched_at: string
}

export interface EmbeddingInfoDetail {
  count: number
  generated_at: string
  model_name?: string
}

export interface FetchResult {
  success: boolean
  count?: number
  error?: string
}

export interface EmbeddingResult {
  success: boolean
  generated_count?: number
  error?: string
}

const dateIndexes = ref<DateIndex[]>([])
const embeddingIndexes = ref<EmbeddingIndex[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const fetchingDates = ref<Set<string>>(new Set())
const generatingEmbeddingDates = ref<Set<string>>(new Set())
let lastFetchTime = 0
const CACHE_DURATION = 5000

export function useDateIndexes() {
  const dateIndexMap = computed(() => {
    const map = new Map<string, number>()
    dateIndexes.value.forEach(idx => {
      map.set(idx.date, idx.total_count)
    })
    return map
  })

  const storedDatesMap = computed(() => {
    const map = new Map<string, number>()
    dateIndexes.value.forEach(idx => {
      if (idx.total_count > 0) {
        map.set(idx.date, idx.total_count)
      }
    })
    return map
  })

  const embeddingIndexMap = computed(() => {
    const map = new Map<string, { count: number; model_name?: string }>()
    embeddingIndexes.value.forEach(idx => {
      map.set(idx.date, { count: idx.total_count, model_name: idx.model_name })
    })
    return map
  })

  const dateIndexInfoMap = computed(() => {
    const map = new Map<string, DateInfoDetail>()
    dateIndexes.value.forEach(idx => {
      map.set(idx.date, { count: idx.total_count, fetched_at: idx.fetched_at })
    })
    return map
  })

  const embeddingIndexInfoMap = computed(() => {
    const map = new Map<string, EmbeddingInfoDetail>()
    embeddingIndexes.value.forEach(idx => {
      map.set(idx.date, { count: idx.total_count, generated_at: idx.generated_at, model_name: idx.model_name })
    })
    return map
  })

  const totalDays = computed(() => {
    return dateIndexes.value.filter(idx => idx.total_count > 0).length
  })

  const totalPapers = computed(() => {
    return dateIndexes.value.reduce((sum, idx) => sum + idx.total_count, 0)
  })

  const totalEmbeddedDays = computed(() => {
    return embeddingIndexes.value.length
  })

  const fetchDateIndexes = async (forceRefresh = false) => {
    const now = Date.now()
    if (!forceRefresh && now - lastFetchTime < CACHE_DURATION && dateIndexes.value.length > 0) {
      return dateIndexes.value
    }

    loading.value = true
    error.value = null

    try {
      const [dateResult, embeddingResult] = await Promise.all([
        arxivBackendAPI.getDateIndexes(),
        arxivBackendAPI.getEmbeddingIndexes()
      ])
      dateIndexes.value = dateResult
      embeddingIndexes.value = embeddingResult.indexes || []
      lastFetchTime = now
      return dateIndexes.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch date indexes'
      console.error('Failed to fetch date indexes:', err)
      return []
    } finally {
      loading.value = false
    }
  }

  const refreshDateIndexes = async () => {
    return fetchDateIndexes(true)
  }

  const getPaperCount = (date: string): number => {
    return dateIndexMap.value.get(date) ?? 0
  }

  const hasStoredPapers = (date: string): boolean => {
    return getPaperCount(date) > 0
  }

  const hasEmbedding = (date: string): boolean => {
    return embeddingIndexMap.value.has(date)
  }

  const isFetching = (date: string): boolean => {
    return fetchingDates.value.has(date)
  }

  const isGeneratingEmbedding = (date: string): boolean => {
    return generatingEmbeddingDates.value.has(date)
  }

  const fetchDate = async (date: string): Promise<FetchResult> => {
    if (fetchingDates.value.has(date)) {
      return { success: false, error: 'Already fetching' }
    }
    
    const newSet = new Set(fetchingDates.value)
    newSet.add(date)
    fetchingDates.value = newSet
    
    try {
      const result = await arxivBackendAPI.fetchPapersForDate(date)
      
      if (result.success) {
        await refreshDateIndexes()
        return { success: true, count: result.count }
      } else {
        return { success: false, error: result.error }
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to fetch papers'
      console.error('Failed to fetch papers:', err)
      return { success: false, error: errorMsg }
    } finally {
      const removeSet = new Set(fetchingDates.value)
      removeSet.delete(date)
      fetchingDates.value = removeSet
    }
  }

  const generateEmbedding = async (date: string, force: boolean = false): Promise<EmbeddingResult> => {
    if (generatingEmbeddingDates.value.has(date)) {
      return { success: false, error: 'Already generating' }
    }
    
    const newSet = new Set(generatingEmbeddingDates.value)
    newSet.add(date)
    generatingEmbeddingDates.value = newSet
    
    try {
      const result = await arxivBackendAPI.generateEmbeddings({ date, force })
      
      if (result.success) {
        await refreshDateIndexes()
        return { success: true, generated_count: result.generated_count }
      } else {
        return { success: false, error: result.error }
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to generate embeddings'
      console.error('Failed to generate embeddings:', err)
      return { success: false, error: errorMsg }
    } finally {
      const removeSet = new Set(generatingEmbeddingDates.value)
      removeSet.delete(date)
      generatingEmbeddingDates.value = removeSet
    }
  }

  return {
    dateIndexes,
    embeddingIndexes,
    dateIndexMap,
    embeddingIndexMap,
    dateIndexInfoMap,
    embeddingIndexInfoMap,
    storedDatesMap,
    loading,
    error,
    fetchingDates,
    generatingEmbeddingDates,
    totalDays,
    totalPapers,
    totalEmbeddedDays,
    fetchDateIndexes,
    refreshDateIndexes,
    getPaperCount,
    hasStoredPapers,
    hasEmbedding,
    isFetching,
    isGeneratingEmbedding,
    fetchDate,
    generateEmbedding
  }
}

export function useDayTooltip(
  dateIndexInfoMap: ComputedRef<Map<string, DateInfoDetail>>,
  embeddingIndexInfoMap: ComputedRef<Map<string, EmbeddingInfoDetail>>
) {
  const tooltipDate = ref<string | null>(null)
  const tooltipPosition = ref({ x: 0, y: 0 })

  const tooltipDateInfo = computed(() => {
    if (!tooltipDate.value) return null
    return dateIndexInfoMap.value.get(tooltipDate.value) || null
  })

  const tooltipEmbeddingInfo = computed(() => {
    if (!tooltipDate.value) return null
    return embeddingIndexInfoMap.value.get(tooltipDate.value) || null
  })

  const showTooltip = (date: string, x: number, y: number) => {
    tooltipDate.value = date
    tooltipPosition.value = { x, y }
  }

  const hideTooltip = () => {
    tooltipDate.value = null
  }

  const isTooltipVisible = computed(() => {
    return !!tooltipDate.value && (!!tooltipDateInfo.value || !!tooltipEmbeddingInfo.value)
  })

  return {
    tooltipDate,
    tooltipPosition,
    tooltipDateInfo,
    tooltipEmbeddingInfo,
    isTooltipVisible,
    showTooltip,
    hideTooltip
  }
}
