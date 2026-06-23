import { ref, computed, watch } from 'vue'
import { useToastStore } from '@/stores/toast-store'
import { useBookmarkStore } from '@/stores/bookmark-store'
import { useDownloadStore } from '@/stores/download-store'
import { useConfigStore } from '@/stores/config-store'
import { listingsAPI } from '@/services/listings'
import { categories, CATEGORY_GROUPS } from '@/utils/categoryColors'
import type { Paper } from '@/types'

export type ListingTab = 'new' | 'cross' | 'replacement'

export function useListings() {
  const configStore = useConfigStore()
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
  const pageSize = ref(50)
  const pageSizeOptions = [50, 100, 200, 500, 1000, 2000]
  const paginatedTotal = ref(0)
  
  const filterCategory = ref<string | null>(null)
  const isFilterDrawerOpen = ref(false)
  const filterHasCodeUrl = ref(false)
  
  const papersWithCodeNew = ref<Paper[]>([])
  const papersWithCodeCross = ref<Paper[]>([])
  const papersWithCodeReplacement = ref<Paper[]>([])
  const isLoadingCodeFilter = ref(false)
  let lastCheckedPaperIds: string = ''
  
  const toastStore = useToastStore()
  const bookmarkStore = useBookmarkStore()
  const downloadStore = useDownloadStore()

  const currentPapers = ref<Paper[]>([])

  const totalCounts = computed(() => {
    if (filterHasCodeUrl.value) {
      return {
        new: papersWithCodeNew.value.length,
        cross: papersWithCodeCross.value.length,
        replacement: papersWithCodeReplacement.value.length
      }
    }

    return {
      new: newPapers.value.length,
      cross: crossPapers.value.length,
      replacement: replacementPapers.value.length
    }
  })

  const getTabPapers = (tab: ListingTab): Paper[] => {
    if (filterHasCodeUrl.value) {
      if (tab === 'new') return papersWithCodeNew.value
      if (tab === 'cross') return papersWithCodeCross.value
      if (tab === 'replacement') return papersWithCodeReplacement.value
    } else {
      if (tab === 'new') return newPapers.value
      if (tab === 'cross') return crossPapers.value
      if (tab === 'replacement') return replacementPapers.value
    }
    return []
  }

  const categoryCounts = computed(() => {
    const papers = getTabPapers(activeTab.value)
    const counts: Record<string, number> = {}
    for (const paper of papers) {
      const category = paper.primaryCategory
      if (category) {
        counts[category] = (counts[category] || 0) + 1
      }
    }
    return counts
  })

  const filteredPapers = computed(() => {
    let papers = getTabPapers(activeTab.value)

    // If no filter or filter is the default subject wildcard, return all papers
    if (!filterCategory.value) {
      return papers
    }

    // Check if filter is a subject wildcard (e.g., 'cs*', 'q-fin*', 'stat*')
    const isSubjectWildcard = CATEGORY_GROUPS.some(g => g.wildcard === filterCategory.value)
    if (isSubjectWildcard) {
      return papers
    }

    // Handle 'other' filter - papers not in any known category of the current subject
    if (filterCategory.value === 'other') {
      const currentGroup = CATEGORY_GROUPS.find(g => g.id === configStore.defaultSubject)
      const knownCategoryIds = currentGroup ? currentGroup.categories.map(cat => cat.id) : categories.map(cat => cat.id)
      return papers.filter(paper => !knownCategoryIds.includes(paper.primaryCategory))
    }

    // Filter by specific category
    return papers.filter(paper => paper.primaryCategory === filterCategory.value)
  })

  const totalItems = computed(() => {
    return filteredPapers.value.length
  })

  const totalPages = computed(() => {
    return Math.ceil(totalItems.value / pageSize.value)
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
    const page = currentPage.value
    const papers = filteredPapers.value
    
    const start = (page - 1) * pageSize.value
    const end = start + pageSize.value
    currentPapers.value = papers.slice(start, end)
  }

  watch([activeTab, currentPage, pageSize, filterCategory, filterHasCodeUrl, newPapers, crossPapers, replacementPapers, papersWithCodeNew, papersWithCodeCross, papersWithCodeReplacement], () => {
    updateCurrentPapers()
  }, { immediate: true })

  watch(currentPage, (newPage) => {
    pageInput.value = newPage
  }, { immediate: true })

  watch(currentPapers, async (papers) => {
    if (papers.length > 0) {
      const paperIds = papers.map(p => p.id).filter(Boolean).sort().join(',')
      if (paperIds && paperIds !== lastCheckedPaperIds) {
        lastCheckedPaperIds = paperIds
        const checkIds = papers.map(p => p.id).filter(Boolean)
        await bookmarkStore.checkBookmarksBatch(checkIds)
        await downloadStore.checkDownloadsBatch(checkIds)
      }
    }
  }, { immediate: true })

  const refreshListings = async (date?: string) => {
    isLoadingListings.value = true
    listingsError.value = null

    try {
      const result = await listingsAPI.getLatestListings(date, configStore.defaultSubject)
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
      const result = await listingsAPI.fetchNewListings(configStore.defaultSubject)

      if (result.success) {
        toastStore.showSuccess(
          `Fetched ${result.total_count} papers from ${result.subject}: ${result.new_count} new, ${result.cross_count} cross, ${result.replacement_count} replacement`
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
    filterCategory.value = null
  }

  const toggleFilterDrawer = () => {
    isFilterDrawerOpen.value = !isFilterDrawerOpen.value
  }

  const closeFilterDrawer = () => {
    isFilterDrawerOpen.value = false
  }

  const handleFilterCategorySelect = (categoryId: string | null) => {
    filterCategory.value = categoryId
    currentPage.value = 1
    pageInput.value = 1
  }

  const fetchPapersWithCode = async (date: string) => {
    isLoadingCodeFilter.value = true
    try {
      const result = await listingsAPI.getPapersWithCode(date)
      papersWithCodeNew.value = result.new
      papersWithCodeCross.value = result.cross
      papersWithCodeReplacement.value = result.replacement
      listingsDate.value = result.date
    } catch (e) {
      console.error('Error fetching papers with code:', e)
    } finally {
      isLoadingCodeFilter.value = false
    }
  }

  const toggleCodeUrlFilter = async () => {
    const newValue = !filterHasCodeUrl.value
    
    if (newValue && listingsDate.value) {
      await fetchPapersWithCode(listingsDate.value)
      filterHasCodeUrl.value = true
    } else {
      await refreshListings(selectedDate.value || undefined)
      filterHasCodeUrl.value = newValue
    }
    
    currentPage.value = 1
    pageInput.value = 1
  }

  const changePageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    pageInput.value = 1
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

  const handleRefresh = async () => {
    if (filterHasCodeUrl.value && listingsDate.value) {
      await fetchPapersWithCode(listingsDate.value)
    } else {
      await refreshListings(selectedDate.value || undefined)
    }
  }

  const onDateChange = async () => {
    currentPage.value = 1
    if (filterHasCodeUrl.value && selectedDate.value) {
      await fetchPapersWithCode(selectedDate.value)
    } else {
      await refreshListings(selectedDate.value || undefined)
    }
  }

  const clearDateFilter = async () => {
    selectedDate.value = ''
    currentPage.value = 1
    filterHasCodeUrl.value = false
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
    pageSizeOptions,
    paginatedTotal,
    totalCounts,
    currentPapers,
    pageInput,
    totalItems,
    totalPages,
    visiblePages,
    switchTab,
    changePageSize,
    goToPage,
    jumpToPage,
    handleRefresh,
    onDateChange,
    clearDateFilter,
    initListings,
    filterCategory,
    categoryCounts,
    isFilterDrawerOpen,
    toggleFilterDrawer,
    closeFilterDrawer,
    handleFilterCategorySelect,
    filterHasCodeUrl,
    toggleCodeUrlFilter,
    isLoadingCodeFilter
  }
}
