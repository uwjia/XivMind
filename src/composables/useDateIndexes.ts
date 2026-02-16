import { ref, computed } from 'vue'
import { arxivBackendAPI } from '../services/arxivBackend'

interface DateIndex {
  date: string
  total_count: number
  fetched_at: string
}

const dateIndexes = ref<DateIndex[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
let lastFetchTime = 0
const CACHE_DURATION = 5000 // 5 seconds cache

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

  const totalDays = computed(() => {
    return dateIndexes.value.filter(idx => idx.total_count > 0).length
  })

  const totalPapers = computed(() => {
    return dateIndexes.value.reduce((sum, idx) => sum + idx.total_count, 0)
  })

  const fetchDateIndexes = async (forceRefresh = false) => {
    const now = Date.now()
    if (!forceRefresh && now - lastFetchTime < CACHE_DURATION && dateIndexes.value.length > 0) {
      return dateIndexes.value
    }

    loading.value = true
    error.value = null

    try {
      dateIndexes.value = await arxivBackendAPI.getDateIndexes()
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

  return {
    dateIndexes,
    dateIndexMap,
    storedDatesMap,
    loading,
    error,
    totalDays,
    totalPapers,
    fetchDateIndexes,
    refreshDateIndexes,
    getPaperCount,
    hasStoredPapers
  }
}
