import { ref, computed, type Ref } from 'vue'
import type { ViewMode } from '@/types/pdf'

export function usePdfNavigation(totalPages: Ref<number>) {
  const currentPage = ref(1)
  const viewMode = ref<ViewMode>('continuous')
  const scrollPosition = ref(0)
  const isUserNavigating = ref(false)

  const canGoPrev = computed(() => currentPage.value > 1)
  const canGoNext = computed(() => currentPage.value < totalPages.value)
  const progress = computed(() => {
    if (totalPages.value === 0) return 0
    return Math.round((currentPage.value / totalPages.value) * 100)
  })

  function goToPage(pageNumber: number) {
    console.log('[usePdfNavigation] goToPage called with:', pageNumber, 'totalPages:', totalPages.value, 'currentPage before:', currentPage.value)
    if (pageNumber >= 1 && pageNumber <= totalPages.value) {
      isUserNavigating.value = true
      currentPage.value = pageNumber
    } else {
      console.log('[usePdfNavigation] goToPage: page number out of range')
    }
  }

  function goToPrevPage() {
    if (canGoPrev.value) {
      isUserNavigating.value = true
      currentPage.value--
    }
  }

  function goToNextPage() {
    if (canGoNext.value) {
      isUserNavigating.value = true
      currentPage.value++
    }
  }

  function goToFirstPage() {
    isUserNavigating.value = true
    currentPage.value = 1
  }

  function goToLastPage() {
    if (totalPages.value > 0) {
      isUserNavigating.value = true
      currentPage.value = totalPages.value
    }
  }

  function toggleViewMode() {
    viewMode.value = viewMode.value === 'single' ? 'continuous' : 'single'
  }

  function setViewMode(mode: ViewMode) {
    viewMode.value = mode
  }

  function updateCurrentPageFromScroll(visiblePage: number) {
    if (viewMode.value === 'continuous' && visiblePage !== currentPage.value) {
      currentPage.value = visiblePage
      isUserNavigating.value = false
    }
  }

  function clearUserNavigation() {
    isUserNavigating.value = false
  }

  return {
    currentPage,
    viewMode,
    scrollPosition,
    isUserNavigating,
    canGoPrev,
    canGoNext,
    progress,
    goToPage,
    goToPrevPage,
    goToNextPage,
    goToFirstPage,
    goToLastPage,
    toggleViewMode,
    setViewMode,
    updateCurrentPageFromScroll,
    clearUserNavigation,
  }
}
