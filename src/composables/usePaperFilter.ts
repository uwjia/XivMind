import { ref, computed, toRefs } from 'vue'
import { usePaperStore } from '../stores/paper-store'
import { useConfigStore } from '../stores/config-store'
import { useToastStore } from '../stores/toast-store'
import { useDateIndexes } from './useDateIndexes'

const isDatePickerOpen = ref(false)
const isCategoryPickerOpen = ref(false)

export function usePaperFilter() {
  const paperStore = usePaperStore()
  const configStore = useConfigStore()
  const toastStore = useToastStore()
  const { refreshDateIndexes } = useDateIndexes()

  const { currentPage } = toRefs(paperStore)
  
  const selectedCategory = computed(() => paperStore.selectedCategory)
  const selectedDate = computed(() => paperStore.selectedDate)
  const loading = computed(() => paperStore.loading)
  const error = computed(() => paperStore.error)

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
      
      const category = selectedCategory.value === 'all' ? 'cs*' : selectedCategory.value
      const dateValue = selectedDate.value
      
      const fetchDefault = () => paperStore.fetchPapers({ 
        category, 
        maxResults: configStore.maxResults, 
        start: startIndex 
      })

      const fetchByDateRange = (startTimestamp: string, endTimestamp: string) => 
        paperStore.fetchPapersByDateRange(startTimestamp, endTimestamp, category, configStore.maxResults, startIndex)
      
      let dateForQuery: Date | null = null
      if (dateValue instanceof Date) {
        dateForQuery = dateValue
      } else if (dateValue && typeof dateValue === 'object' && 'startDate' in dateValue && dateValue.startDate) {
        dateForQuery = new Date(dateValue.startDate)
      }
      
      if (dateForQuery && !isNaN(dateForQuery.getTime())) {
        const { startTimestamp, endTimestamp } = getDateTimestamps(dateForQuery)
        await fetchByDateRange(startTimestamp, endTimestamp)
      } else {
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
    goToPage
  }
}
