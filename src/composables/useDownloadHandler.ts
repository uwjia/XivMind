import { useDownloadStore } from '../stores/download-store'
import { useToastStore } from '../stores/toast-store'
import { apiService } from '../services/api'

interface DownloadParams {
  paperId: string
  arxivId?: string
  title: string
  pdfUrl: string
}

export function useDownloadHandler() {
  const downloadStore = useDownloadStore()
  const toastStore = useToastStore()

  const getStatus = (paperId: string): string => {
    const task = downloadStore.tasks.find(t => t.paper_id === paperId)
    return task?.status || 'none'
  }

  const getProgress = (paperId: string): number => {
    const task = downloadStore.tasks.find(t => t.paper_id === paperId)
    return task?.progress || 0
  }

  const getTask = (paperId: string) => {
    return downloadStore.tasks.find(t => t.paper_id === paperId)
  }

  const handleDownload = async (params: DownloadParams): Promise<boolean> => {
    if (!params.pdfUrl || !params.paperId) {
      toastStore.showError('No PDF URL available')
      return false
    }

    const existingTask = downloadStore.tasks.find(t => t.paper_id === params.paperId)

    if (existingTask) {
      switch (existingTask.status) {
        case 'failed':
          try {
            await downloadStore.retryTask(existingTask.id)
            toastStore.showSuccess('Download retry started')
            return true
          } catch (error) {
            console.error('Failed to retry download:', error)
            toastStore.showError('Failed to retry download')
            return false
          }
        case 'downloading':
          toastStore.showInfo('Download already in progress')
          return false
        case 'completed':
          try {
            await apiService.openDownloadFile(existingTask.id)
            return true
          } catch (error) {
            console.error('Failed to open file:', error)
            toastStore.showError('Failed to open file')
            return false
          }
        default:
          toastStore.showInfo('Download already queued')
          return false
      }
    }

    try {
      await downloadStore.createTask({
        paper_id: params.paperId,
        arxiv_id: params.arxivId,
        title: params.title,
        pdf_url: params.pdfUrl,
      })
      toastStore.showSuccess('Download task added to queue')
      return true
    } catch (error) {
      console.error('Failed to create download task:', error)
      toastStore.showError('Failed to create download task')
      return false
    }
  }

  const getStatusTitle = (paperId: string): string => {
    const status = getStatus(paperId)
    const progress = getProgress(paperId)
    switch (status) {
      case 'downloading':
        return `Downloading... ${progress}%`
      case 'completed':
        return 'Download completed - click to open'
      case 'failed':
        return 'Download failed - click to retry'
      case 'pending':
        return 'Download pending...'
      default:
        return 'Download PDF'
    }
  }

  return { 
    getStatus, 
    getProgress, 
    getTask,
    handleDownload,
    getStatusTitle
  }
}
