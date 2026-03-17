import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService, type DownloadTask, type DownloadTaskData } from '@/services/api'
import { API_BASE_URL } from '@/services/config'

type ProgressCallback = (taskId: string, progress: number, status: string) => void

class DownloadWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private progressCallbacks: ProgressCallback[] = []
  private baseUrl: string

  constructor() {
    if (API_BASE_URL) {
      this.baseUrl = `ws://localhost:8000/api/downloads/ws`
    } else {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      this.baseUrl = `${protocol}//${window.location.host}/api/downloads/ws`
    }
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.baseUrl)

        this.ws.onopen = () => {
          console.log('WebSocket connected to download service')
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (data.type === 'progress') {
              this.progressCallbacks.forEach(cb => cb(data.task_id, data.progress, data.status))
            }
          } catch (e) {
            console.error('Failed to parse WebSocket message:', e)
          }
        }

        this.ws.onerror = () => {
          console.log('WebSocket connection error (backend may not be running)')
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            console.log('WebSocket connection failed, will attempt reconnect...')
          }
          reject(new Error('WebSocket connection failed'))
        }

        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.attemptReconnect()
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      setTimeout(() => {
        this.connect().catch(e => console.error('Reconnect failed:', e))
      }, this.reconnectDelay)
    }
  }

  subscribe(taskId: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'subscribe', task_id: taskId }))
    }
  }

  onProgress(callback: ProgressCallback) {
    this.progressCallbacks.push(callback)
  }

  removeProgressCallback(callback: ProgressCallback) {
    const index = this.progressCallbacks.indexOf(callback)
    if (index > -1) {
      this.progressCallbacks.splice(index, 1)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

const downloadWs = new DownloadWebSocket()

export const useDownloadStore = defineStore('download', () => {
  const tasks = ref<DownloadTask[]>([])
  const total = ref(0)
  const completedCount = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const wsConnected = ref(false)
  const initialized = ref(false)
  const downloadedIds = ref<Set<string>>(new Set())

  const addDownloadedId = (paperId: string) => {
    const newSet = new Set(downloadedIds.value)
    newSet.add(paperId)
    downloadedIds.value = newSet
  }

  const removeDownloadedId = (paperId: string) => {
    const newSet = new Set(downloadedIds.value)
    newSet.delete(paperId)
    downloadedIds.value = newSet
  }

  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const setError = (value: string | null) => {
    error.value = value
  }

  const init = async () => {
    if (initialized.value) return
    
    initialized.value = true
    await connectWebSocket()
  }

  const connectWebSocket = async () => {
    if (!wsConnected.value) {
      try {
        await downloadWs.connect()
        wsConnected.value = true
        
        downloadWs.onProgress(async (taskId, progress, status) => {
          const task = tasks.value.find(t => t.id === taskId)
          if (task) {
            const previousStatus = task.status
            task.progress = progress
            task.status = status as 'pending' | 'downloading' | 'completed' | 'failed'
            
            if (status === 'completed' && previousStatus !== 'completed') {
              completedCount.value += 1
            }
            
            if (status === 'completed' || status === 'failed') {
              try {
                const updatedTask = await apiService.getDownloadTask(taskId)
                const existingIndex = tasks.value.findIndex(t => t.id === taskId)
                if (existingIndex >= 0) {
                  tasks.value[existingIndex] = updatedTask
                  if (status === 'completed') {
                    addDownloadedId(task.paper_id)
                  }
                }
              } catch (e) {
                console.error('Failed to fetch updated task:', e)
              }
            }
          }
        })
      } catch (e) {
        console.error('Failed to connect WebSocket:', e)
      }
    }
  }

  const disconnectWebSocket = () => {
    downloadWs.disconnect()
    wsConnected.value = false
  }

  const createTask = async (data: DownloadTaskData) => {
    try {
      setLoading(true)
      setError(null)
      const result = await apiService.createDownloadTask(data)
      const existingIndex = tasks.value.findIndex(t => t.id === result.id)
      if (existingIndex >= 0) {
        tasks.value[existingIndex] = result
      } else {
        tasks.value.unshift(result)
      }
      
      if (wsConnected.value) {
        downloadWs.subscribe(result.id)
      }
      
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchTasks = async (limit: number = 1000, offset: number = 0) => {
    try {
      setLoading(true)
      setError(null)
      const result = await apiService.getDownloadTasks(limit, offset)
      tasks.value = result.items
      total.value = result.total
      completedCount.value = result.completed_count
      result.items.forEach(item => {
        if (item.status === 'completed') {
          addDownloadedId(item.paper_id)
        }
      })
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getTask = async (taskId: string) => {
    try {
      const result = await apiService.getDownloadTask(taskId)
      const existingIndex = tasks.value.findIndex(t => t.id === taskId)
      if (existingIndex >= 0) {
        tasks.value[existingIndex] = result
      }
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    }
  }

  const deleteTask = async (taskId: string) => {
    try {
      setLoading(true)
      setError(null)
      const task = tasks.value.find(t => t.id === taskId)
      await apiService.deleteDownloadTask(taskId)
      const taskIndex = tasks.value.findIndex(t => t.id === taskId)
      if (taskIndex >= 0) {
        tasks.value.splice(taskIndex, 1)
        if (task && task.status === 'completed') {
          completedCount.value = Math.max(0, completedCount.value - 1)
          removeDownloadedId(task.paper_id)
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const retryTask = async (taskId: string) => {
    try {
      setLoading(true)
      setError(null)
      const result = await apiService.retryDownloadTask(taskId)
      const existingIndex = tasks.value.findIndex(t => t.id === taskId)
      if (existingIndex >= 0) {
        tasks.value[existingIndex] = result
      }
      
      if (wsConnected.value) {
        downloadWs.subscribe(taskId)
      }
      
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const cancelTask = async (taskId: string) => {
    try {
      const result = await apiService.cancelDownloadTask(taskId)
      const existingIndex = tasks.value.findIndex(t => t.id === taskId)
      if (existingIndex >= 0) {
        tasks.value[existingIndex] = result
      }
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    }
  }

  const updateTaskInList = (task: DownloadTask) => {
    const existingIndex = tasks.value.findIndex(t => t.id === task.id)
    if (existingIndex >= 0) {
      tasks.value[existingIndex] = task
    }
  }

  const getPendingTasks = () => {
    return tasks.value.filter(t => t.status === 'pending' || t.status === 'downloading')
  }

  const getCompletedTasks = () => {
    return tasks.value.filter(t => t.status === 'completed')
  }

  const getFailedTasks = () => {
    return tasks.value.filter(t => t.status === 'failed')
  }

  const checkDownload = async (paperId: string) => {
    try {
      const result = await apiService.checkDownload(paperId)
      if (result.is_downloaded) {
        addDownloadedId(paperId)
      } else {
        removeDownloadedId(paperId)
      }
      return result.is_downloaded
    } catch (err) {
      console.error('Error checking download:', err)
      return false
    }
  }

  const checkDownloadsBatch = async (paperIds: string[]) => {
    try {
      const result = await apiService.checkDownloadsBatch(paperIds)
      const newSet = new Set(downloadedIds.value)
      Object.entries(result.downloads).forEach(([paperId, isDownloaded]) => {
        if (isDownloaded) {
          newSet.add(paperId)
        } else {
          newSet.delete(paperId)
        }
      })
      downloadedIds.value = newSet
      return result.downloads
    } catch (err) {
      console.error('Error checking downloads batch:', err)
      return {}
    }
  }

  const isDownloaded = (paperId: string) => {
    return downloadedIds.value.has(paperId)
  }

  const syncLocalFiles = async () => {
    try {
      setLoading(true)
      const result = await apiService.syncLocalFiles()
      // await fetchTasks()
      return result
    } catch (err) {
      console.error('Error syncing local files:', err)
      setError(err instanceof Error ? err.message : 'Failed to sync local files')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchMissingFiles = async (limit: number = 100, offset: number = 0) => {
    try {
      setLoading(true)
      const result = await apiService.getMissingFiles(limit, offset)
      tasks.value = result.items
      total.value = result.total
      return result
    } catch (err) {
      console.error('Error fetching missing files:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch missing files')
      return { items: [], total: 0, completed_count: 0 }
    } finally {
      setLoading(false)
    }
  }

  const fetchIncomplete = async (limit: number = 100, offset: number = 0) => {
    try {
      setLoading(true)
      const result = await apiService.getIncomplete(limit, offset)
      tasks.value = result.items
      total.value = result.total
      completedCount.value = result.completed_count
      return result
    } catch (err) {
      console.error('Error fetching incomplete tasks:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch incomplete tasks')
      return { items: [], total: 0, completed_count: 0 }
    } finally {
      setLoading(false)
    }
  }

  return {
    tasks,
    total,
    completedCount,
    loading,
    error,
    wsConnected,
    initialized,
    init,
    connectWebSocket,
    disconnectWebSocket,
    createTask,
    fetchTasks,
    getTask,
    deleteTask,
    retryTask,
    cancelTask,
    updateTaskInList,
    getPendingTasks,
    getCompletedTasks,
    getFailedTasks,
    setLoading,
    setError,
    checkDownload,
    checkDownloadsBatch,
    isDownloaded,
    syncLocalFiles,
    fetchMissingFiles,
    fetchIncomplete,
  }
})
