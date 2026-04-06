import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { readingHistoryAPI, type ReadingHistoryItem } from '@/services/readingHistory'
import { useNoteStore } from '@/stores/note-store'

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
  const needsRefresh = ref(false)

  const totalCount = computed(() => history.value.length)

  const fetchHistory = async (limit: number = 20) => {
    isLoading.value = true
    error.value = null
    try {
      history.value = await readingHistoryAPI.getReadingHistory(limit)
      needsRefresh.value = false
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch reading history'
    } finally {
      isLoading.value = false
    }
  }

  const markNeedsRefresh = () => {
    needsRefresh.value = true
  }

  const showPanel = () => {
    useNoteStore().hidePanel()
    isVisible.value = true
    if (history.value.length === 0 || needsRefresh.value) {
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
    const panelWidth = size.value.width
    const newX = Math.max(10, historyBtnPosition.value.x - panelWidth)
    const newY = historyBtnPosition.value.y + 8
    position.value = { x: newX, y: newY }
    hasUserMovedPanel.value = false
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
    needsRefresh,
    totalCount,
    fetchHistory,
    markNeedsRefresh,
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
