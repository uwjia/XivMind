import { ref, computed, toRefs } from 'vue'
import { usePaperStore } from '@/stores/paper-store'
import { useConfigStore } from '@/stores/config-store'
import { useToastStore } from '@/stores/toast-store'
import { useDateIndexes } from '@/composables/useDateIndexes'
import type { Paper } from '@/types'
import { categories, CATEGORY_GROUPS } from '@/utils/categoryColors'

const isDatePickerOpen = ref(false)
const isCategoryPickerOpen = ref(false)

const isFilterDrawerOpen = ref(false)

export function usePaperFilter() {
  const paperStore = usePaperStore()
  const configStore = useConfigStore()
  const toastStore = useToastStore()
  const { fetchDateIndexes, getLatestStoredDate, refreshDateIndexes } = useDateIndexes()

  const { currentPage } = toRefs(paperStore)
  
  const selectedCategory = computed(() => paperStore.selectedCategory)
  const selectedDate = computed(() => paperStore.selectedDate)
  const loading = computed(() => paperStore.loading)
  const error = computed(() => paperStore.error)
  const totalPapers = computed(() => paperStore.totalPapers)

  
const localFilterCategory = ref<string | null>(null)

const allPapers = computed<Paper[]>(() => {
  return paperStore.getFilteredPapers()
})

// Total papers count for category tree (actual papers in current view)
const categoryTreeTotalPapers = computed(() => allPapers.value.length)

const handleFilterCategorySelect = (categoryId: string | null) => {
  localFilterCategory.value = categoryId
}

const filteredPapers = computed<Paper[]>(() => {
  const papers = allPapers.value
  const defaultWildcard = `${configStore.defaultSubject}*`

  // Check if filter is a subject wildcard (e.g., 'cs*', 'q-fin*', 'stat*')
  const isSubjectWildcard = CATEGORY_GROUPS.some(g => g.wildcard === localFilterCategory.value)

  if (!localFilterCategory.value || isSubjectWildcard) {
    return papers
  }
  if (localFilterCategory.value === 'other') {
    const currentGroup = CATEGORY_GROUPS.find(g => g.id === configStore.defaultSubject)
    const knownCategoryIds = currentGroup ? currentGroup.categories.map(cat => cat.id) : categories.map(cat => cat.id)
    return papers.filter(paper => !knownCategoryIds.includes(paper.primaryCategory))
  }
  return papers.filter(paper => paper.primaryCategory === localFilterCategory.value)
})

const categoryCounts = computed(() => {
  const counts: Record<string, number> = {}
  for (const paper of allPapers.value) {
    const category = paper.primaryCategory
    if (category) {
      counts[category] = (counts[category] || 0) + 1
    }
  }
  return counts
})

const filterDescription = computed(() => {
  const parts = []
  
  if (selectedCategory.value !== 'all') {
    const category = categories.find(cat => cat.id === selectedCategory.value)
    if (category) {
      parts.push(`${selectedCategory.value} (${category.name})`)
    } else {
      parts.push(selectedCategory.value)
    }
  }
  
  if (selectedDate.value !== 'all') {
    if (selectedDate.value instanceof Date) {
      const year = selectedDate.value.getFullYear()
      const month = String(selectedDate.value.getMonth() + 1).padStart(2, '0')
      const day = String(selectedDate.value.getDate()).padStart(2, '0')
      parts.push(`${year}-${month}-${day}`)
    } else {
      parts.push(selectedDate.value)
    }
  }
  
  parts.push(`Page ${ currentPage.value + 1 } of ${filteredPapers.value.length} papers`)
  
  if (totalPapers.value > 0) {
    parts.push(`Total: ${totalPapers.value}`)
  }
  
  return parts.join(' · ')
})

  const toggleDatePicker = () => {
    isDatePickerOpen.value = !isDatePickerOpen.value
  }

  const toggleCategoryPicker = () => {
    isCategoryPickerOpen.value = !isCategoryPickerOpen.value
  }

  const closeDatePicker = () => {
    isDatePickerOpen.value = false
  }

  const closeCategoryPicker = () => {
    isCategoryPickerOpen.value = false
  }

  const getDateTimestamps = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return {
      startTimestamp: `${year}${month}${day}000000`,
      endTimestamp: `${year}${month}${day}235959`
    }
  }

  const loadPapers = async (page?: number) => {
    const targetPage = page !== undefined ? page : currentPage.value
    const startIndex = targetPage * configStore.maxResults

    try {
      console.log('Loading papers...', selectedCategory.value, selectedDate.value, startIndex)
      toastStore.showLoading('Loading papers...')

      const defaultCategory = `${configStore.defaultSubject}*`
      const category = selectedCategory.value === 'all' ? defaultCategory : selectedCategory.value
      const dateValue = selectedDate.value

      let dateForQuery: Date | null = null
      if (dateValue instanceof Date) {
        dateForQuery = dateValue
      } else if (dateValue && typeof dateValue === 'object' && 'startDate' in dateValue && dateValue.startDate) {
        dateForQuery = new Date(dateValue.startDate)
      }

      if (dateForQuery && !isNaN(dateForQuery.getTime())) {
        const { startTimestamp, endTimestamp } = getDateTimestamps(dateForQuery)
        const fetchByDateRange = (startTimestamp: string, endTimestamp: string) =>
          paperStore.fetchPapersByDateRange(startTimestamp, endTimestamp, category, configStore.maxResults, startIndex)
        await fetchByDateRange(startTimestamp, endTimestamp)
      } else {
        // for case when selectedDate is 'all'
        const fetchDefault = () => paperStore.fetchTodayPapersBackend({
          category,
          maxResults: configStore.maxResults,
          start: startIndex
        })
        await fetchDefault()
      }

      toastStore.showSuccess('Papers loaded successfully!')
      window.scrollTo({ top: 0, behavior: 'instant' })

      console.log('Total papers in store:', paperStore.papers.length)
    } catch (err) {
      console.error('Failed to load papers:', err)
      toastStore.showError('Failed to load papers. Please try again.')
    }
  }

  const checkAndLoadPapers = async () => {
    console.log('Checking if papers need to be loaded...')
    console.log('Current papers count:', paperStore.papers.length)
    
    if (paperStore.papers.length === 0) {
      console.log('No papers in store, fetching date indexes first...')
      await fetchDateIndexes()
      
      const latestDate = getLatestStoredDate()
      
      if (latestDate) {
        console.log('Found latest stored date:', latestDate)
        handleDateSelect(new Date(latestDate))
      } else {
        console.log('No stored dates found, loading default papers...')
        loadPapers(0)
      }
    } else {
      console.log('Papers already loaded, skipping fetch')
    }
  }

  const toggleFilterDrawer = () => {
    isFilterDrawerOpen.value = !isFilterDrawerOpen.value
  }

  const closeFilterDrawer = () => {
    isFilterDrawerOpen.value = false
  }

  const goToFirstPage = () => {
    paperStore.setCurrentPage(0)
    loadPapers(0)
  }

  const goToPreviousPage = () => {
    if (currentPage.value > 0) {
      paperStore.setCurrentPage(currentPage.value - 1)
      loadPapers()
    }
  }

  const goToNextPage = () => {
    paperStore.setCurrentPage(currentPage.value + 1)
    loadPapers()
  }

  const goToPage = (targetPage: number) => {
    if (targetPage >= 0) {
      paperStore.setCurrentPage(targetPage)
      loadPapers(targetPage)
    }
  }

  const handleDateSelect = async (value: string | Date | { startDate: string; endDate: string }) => {
    console.log('handleDateSelect called with:', value)
    paperStore.setSelectedDate(value)
    paperStore.setCurrentPage(0)
    await loadPapers(0)
    await refreshDateIndexes()
  }

  const handleCategorySelect = async (value: string) => {
    console.log('handleCategorySelect called with:', value)
    paperStore.setSelectedCategory(value)
    paperStore.setCurrentPage(0)
    await loadPapers(0)
  }

  return {
    currentPage,
    selectedCategory,
    selectedDate,
    loading,
    error,
    totalPapers,
    categoryTreeTotalPapers,
    isDatePickerOpen,
    isCategoryPickerOpen,
    toggleDatePicker,
    toggleCategoryPicker,
    closeDatePicker,
    closeCategoryPicker,
    handleDateSelect,
    handleCategorySelect,
    loadPapers,
    goToFirstPage,
    goToPreviousPage,
    goToNextPage,
    goToPage,
    handleFilterCategorySelect,
    localFilterCategory,
    filteredPapers,
    filterDescription,
    categoryCounts,
    checkAndLoadPapers,
    toggleFilterDrawer,
    closeFilterDrawer,
    isFilterDrawerOpen,
  }
}
