import { ref, computed, watch } from 'vue'
import { useToastStore } from '@/stores/toast-store'
import { useBookmarkStore } from '@/stores/bookmark-store'
import { useDownloadStore } from '@/stores/download-store'
import { listingsAPI } from '@/services/listings'
import type { Paper } from '@/types'

export type ListingTab = 'new' | 'cross' | 'replacement'

export function useListings() {
  const isFetchingListings = ref(false)
  const isLoadingListings = ref(false)
  const listingsError = ref<string | null>(null)
  const listingsDate = ref<string>('')
  const newPapers = ref<Paper[]>([])
  const crossPapers = ref<Paper[]>([])
  const replacementPapers = ref<Paper[]>([])
  
  const activeTab = ref<ListingTab>('new')
  const selectedDate = ref<string>('')
  const currentPage = ref(1)
  const pageInput = ref(1)
  const pageSize = 50
  const paginatedTotal = ref(0)
  
  const toastStore = useToastStore()
  const bookmarkStore = useBookmarkStore()
  const downloadStore = useDownloadStore()

  const currentPapers = ref<Paper[]>([])

  const totalCounts = computed(() => {
    return {
      new: newPapers.value.length,
      cross: crossPapers.value.length,
      replacement: replacementPapers.value.length
    }
  })

  const totalItems = computed(() => {
    const tab = activeTab.value
    if (tab === 'new') return newPapers.value.length
    if (tab === 'cross') return crossPapers.value.length
    if (tab === 'replacement') return replacementPapers.value.length
    return 0
  })

  const totalPages = computed(() => {
    return Math.ceil(totalItems.value / pageSize)
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

  const updateCurrentPapers = () => {
    const tab = activeTab.value
    const page = currentPage.value
    let papers: Paper[]
    
    if (tab === 'new') {
      papers = newPapers.value
    } else if (tab === 'cross') {
      papers = crossPapers.value
    } else if (tab === 'replacement') {
      papers = replacementPapers.value
    } else {
      papers = []
    }
    
    const start = (page - 1) * pageSize
    const end = start + pageSize
    currentPapers.value = papers.slice(start, end)
  }

  watch([activeTab, currentPage, newPapers, crossPapers, replacementPapers], () => {
    updateCurrentPapers()
  }, { immediate: true })

  watch(currentPage, (newPage) => {
    pageInput.value = newPage
  }, { immediate: true })

  watch(currentPapers, async (papers) => {
    if (papers.length > 0) {
      const paperIds = papers.map(p => p.id).filter(Boolean)
      if (paperIds.length > 0) {
        await bookmarkStore.checkBookmarksBatch(paperIds)
        await downloadStore.checkDownloadsBatch(paperIds)
      }
    }
  }, { immediate: true })

  const refreshListings = async (date?: string) => {
    isLoadingListings.value = true
    listingsError.value = null

    try {
      const result = await listingsAPI.getLatestListings(date)
      listingsDate.value = result.date
      newPapers.value = result.new
      crossPapers.value = result.cross
      replacementPapers.value = result.replacement

      if (result.error) {
        listingsError.value = result.error
      }
    } catch (e) {
      listingsError.value = e instanceof Error ? e.message : 'Failed to load listings'
    } finally {
      isLoadingListings.value = false
    }
  }

  const fetchNewListings = async () => {
    if (isFetchingListings.value) return

    isFetchingListings.value = true

    try {
      const result = await listingsAPI.fetchNewListings()

      if (result.success) {
        toastStore.showSuccess(
          `Fetched ${result.total_count} papers: ${result.new_count} new, ${result.cross_count} cross, ${result.replacement_count} replacement`
        )
        return { success: true, result }
      } else {
        toastStore.showError(`Failed to fetch listings: ${result.error || 'Unknown error'}`)
        return { success: false, error: result.error }
      }
    } catch (error) {
      console.error('Error fetching new listings:', error)
      toastStore.showError('Failed to fetch new listings')
      return { success: false, error: 'Unknown error' }
    } finally {
      isFetchingListings.value = false
    }
  }

  const fetchAndRefresh = async () => {
    const result = await fetchNewListings()
    if (result?.success) {
      await refreshListings()
    }
  }

  const switchTab = (tab: ListingTab) => {
    activeTab.value = tab
    currentPage.value = 1
  }

  const goToPage = (page: number) => {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'instant' })
  }

  const jumpToPage = () => {
    let page = pageInput.value
    if (typeof page !== 'number' || isNaN(page)) {
      pageInput.value = currentPage.value
      return
    }
    page = Math.max(1, Math.min(page, totalPages.value))
    pageInput.value = page
    if (page !== currentPage.value) {
      goToPage(page)
    }
  }

  const handleRefresh = () => {
    refreshListings(selectedDate.value || undefined)
  }

  const onDateChange = async () => {
    currentPage.value = 1
    await refreshListings(selectedDate.value || undefined)
  }

  const clearDateFilter = async () => {
    selectedDate.value = ''
    currentPage.value = 1
    await refreshListings()
  }

  const initListings = () => {
    refreshListings()
  }

  return {
    isFetchingListings,
    isLoadingListings,
    listingsError,
    listingsDate,
    newPapers,
    crossPapers,
    replacementPapers,
    refreshListings,
    fetchNewListings,
    fetchAndRefresh,
    activeTab,
    selectedDate,
    currentPage,
    pageSize,
    paginatedTotal,
    totalCounts,
    currentPapers,
    pageInput,
    totalItems,
    totalPages,
    visiblePages,
    switchTab,
    goToPage,
    jumpToPage,
    handleRefresh,
    onDateChange,
    clearDateFilter,
    initListings
  }
}
