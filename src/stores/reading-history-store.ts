import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { readingHistoryAPI, type ReadingHistoryItem } from '@/services/readingHistory'

export const useReadingHistoryStore = defineStore('readingHistory', () => {
  const history = ref<ReadingHistoryItem[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isVisible = ref(false)
  const isMinimized = ref(false)
  const position = ref({ x: 20, y: 80 })
  const size = ref({ width: 360, height: 480 })
  const hasUserMovedPanel = ref(false)
  const historyBtnPosition = ref({ x: 0, y: 0 })

  const totalCount = computed(() => history.value.length)

  const fetchHistory = async (limit: number = 20) => {
    isLoading.value = true
    error.value = null
    try {
      history.value = await readingHistoryAPI.getReadingHistory(limit)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch reading history'
    } finally {
      isLoading.value = false
    }
  }

  const showPanel = () => {
    isVisible.value = true
    if (history.value.length === 0) {
      fetchHistory()
    }
  }

  const hidePanel = () => {
    isVisible.value = false
  }

  const togglePanel = () => {
    if (isVisible.value) {
      hidePanel()
    } else {
      showPanel()
    }
  }

  const toggleMinimize = () => {
    isMinimized.value = !isMinimized.value
  }

  const updatePosition = (x: number, y: number) => {
    position.value = { x, y }
    hasUserMovedPanel.value = true
  }

  const updateSize = (width: number, height: number) => {
    size.value = { width, height }
  }

  const setHistoryBtnPosition = (x: number, y: number) => {
    historyBtnPosition.value = { x, y }
  }

  const resetToDefaultPosition = () => {
    const defaultX = Math.min(
      historyBtnPosition.value.x - size.value.width - 10,
      window.innerWidth - size.value.width - 20
    )
    position.value = {
      x: Math.max(20, defaultX),
      y: 80
    }
  }

  return {
    history,
    isLoading,
    error,
    isVisible,
    isMinimized,
    position,
    size,
    hasUserMovedPanel,
    historyBtnPosition,
    totalCount,
    fetchHistory,
    showPanel,
    hidePanel,
    togglePanel,
    toggleMinimize,
    updatePosition,
    updateSize,
    setHistoryBtnPosition,
    resetToDefaultPosition,
  }
})
