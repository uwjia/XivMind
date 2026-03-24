import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDownloadStore } from '@/stores/download-store'
import { useConfigStore } from '@/stores/config-store'
import { useToastStore } from '@/stores/toast-store'
import { apiService } from '@/services/api'

export type FilterMode = 'all' | 'incomplete' | 'missing'

export function useDownloadActions() {
  const router = useRouter()
  const downloadStore = useDownloadStore()
  const configStore = useConfigStore()
  const toastStore = useToastStore()

  const tasks = computed(() => downloadStore.tasks)
  const total = computed(() => downloadStore.total)
  const completedCount = computed(() => downloadStore.completedCount)
  const loading = computed(() => downloadStore.loading)
  const wsConnected = computed(() => downloadStore.wsConnected)

  const pageSize = computed(() => configStore.maxResults || 20)
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  const currentPage = ref(0)
  const jumpPageInput = ref<string>('')

  const showDeleteConfirm = ref(false)
  const taskToDelete = ref<string | null>(null)
  const taskToDeleteTitle = ref<string>('')

  const filterMode = ref<FilterMode>('all')

  const deleteConfirmMessage = computed(() => {
    if (taskToDeleteTitle.value) {
      return `Are you sure you want to delete the download task for "${taskToDeleteTitle.value}"? This action cannot be undone.`
    }
    return 'Are you sure you want to delete this download task? This action cannot be undone.'
  })

  const fetchTasks = async () => {
    try {
      const offset = currentPage.value * pageSize.value
      if (filterMode.value === 'all') {
        await downloadStore.fetchTasks(pageSize.value, offset)
      } else if (filterMode.value === 'incomplete') {
         await downloadStore.fetchIncomplete(pageSize.value, offset)
      } else if (filterMode.value === 'missing') {
        await downloadStore.fetchMissingFiles(pageSize.value, offset)
      }
    } catch (error) {
      console.error('Failed to fetch download tasks:', error)
      toastStore.showError('Failed to load download tasks')
    }
  }

  const refreshTasks = () => {
    currentPage.value = 0
    fetchTasks()
  }

  const goToFirstPage = () => {
    currentPage.value = 0
    fetchTasks()
  }

  const goToPreviousPage = () => {
    if (currentPage.value > 0) {
      currentPage.value--
      fetchTasks()
    }
  }

  const goToNextPage = () => {
    if (currentPage.value < totalPages.value - 1) {
      currentPage.value++
      fetchTasks()
    }
  }

  const goToPage = (page: number) => {
    if (page >= 0 && page < totalPages.value) {
      currentPage.value = page
      fetchTasks()
    }
  }

  const handleGoToPage = () => {
    const targetPage = parseInt(jumpPageInput.value)
    if (targetPage && targetPage > 0) {
      goToPage(targetPage - 1)
      jumpPageInput.value = ''
    }
  }

  const retryTask = async (taskId: string) => {
    try {
      await downloadStore.retryTask(taskId)
      toastStore.showSuccess('Download retry started')
    } catch (error) {
      console.error('Failed to retry download:', error)
      toastStore.showError('Failed to retry download')
    }
  }

  const cancelTask = async (taskId: string) => {
    try {
      await downloadStore.cancelTask(taskId)
      toastStore.showSuccess('Download cancelled')
    } catch (error) {
      console.error('Failed to cancel download:', error)
      toastStore.showError('Failed to cancel download')
    }
  }

  const deleteTask = (taskId: string) => {
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      taskToDelete.value = taskId
      taskToDeleteTitle.value = task.title
      showDeleteConfirm.value = true
    }
  }

  const confirmDelete = async () => {
    if (!taskToDelete.value) return
    
    try {
      await downloadStore.deleteTask(taskToDelete.value)
      toastStore.showSuccess('Download task deleted')
      if (tasks.value.length === 0 && currentPage.value > 0) {
        currentPage.value--
        fetchTasks()
      }
    } catch (error) {
      console.error('Failed to delete task:', error)
      toastStore.showError('Failed to delete task')
    } finally {
      showDeleteConfirm.value = false
      taskToDelete.value = null
      taskToDeleteTitle.value = ''
    }
  }

  const cancelDelete = () => {
    showDeleteConfirm.value = false
    taskToDelete.value = null
    taskToDeleteTitle.value = ''
  }

  const openFile = async (taskId: string) => {
    try {
      await apiService.openDownloadFile(taskId)
    } catch (error) {
      console.error('Failed to open file:', error)
      toastStore.showError('Failed to open file')
    }
  }

  const goToDetail = (paperId: string) => {
    router.push({ name: 'PaperDetail', params: { id: paperId } })
  }

  const openReader = (paperId: string) => {
    router.push({ name: 'PdfReader', params: { paperId } })
  }

  const syncLocalFiles = async () => {
    try {
      const result = await downloadStore.syncLocalFiles()
      if (result.added > 0) {
        toastStore.showSuccess(`Synced ${result.added} local PDF file(s) to database`)
      } else if (result.skipped > 0) {
        toastStore.showInfo(`All ${result.skipped} file(s) already in database`)
      } else if (result.errors > 0) {
        toastStore.showInfo(`Sync completed with ${result.errors} error(s)`)
      } else {
        toastStore.showInfo('No PDF files found to sync')
      }
      return result
    } catch (error) {
      console.error('Failed to sync local files:', error)
      toastStore.showError('Failed to sync local files')
      throw error
    }
  }

  const setFilterMode = async (mode: FilterMode) => {
    filterMode.value = mode
    currentPage.value = 0
    await fetchTasks()
  }

  return {
    tasks,
    total,
    completedCount,
    loading,
    wsConnected,
    currentPage,
    totalPages,
    pageSize,
    jumpPageInput,
    showDeleteConfirm,
    deleteConfirmMessage,
    filterMode,
    fetchTasks,
    refreshTasks,
    retryTask,
    cancelTask,
    deleteTask,
    confirmDelete,
    cancelDelete,
    openFile,
    goToDetail,
    openReader,
    goToFirstPage,
    goToPreviousPage,
    goToNextPage,
    goToPage,
    handleGoToPage,
    syncLocalFiles,
    setFilterMode,
  }
}
