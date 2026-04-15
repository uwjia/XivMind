import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService, type DownloadTask, type DownloadTaskData } from '@/services/api'
import { API_BASE_URL } from '@/services/config'

type ProgressCallback = (taskId: string, progress: number, status: string) => void
type ConnectionCallback = () => void

class DownloadWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectDelay = 3000
  private progressCallbacks: ProgressCallback[] = []
  private onConnectCallbacks: ConnectionCallback[] = []
  private onDisconnectCallbacks: ConnectionCallback[] = []
  private baseUrl: string
  private isConnecting = false
  private shouldReconnect = true

  constructor() {
    if (API_BASE_URL) {
      this.baseUrl = `ws://localhost:8000/api/downloads/ws`
    } else {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      this.baseUrl = `${protocol}//${window.location.host}/api/downloads/ws`
    }
  }

  connect(): Promise<void> {
    if (this.isConnecting) {
      return Promise.reject(new Error('Already connecting'))
    }
    
    return new Promise((resolve, reject) => {
      this.isConnecting = true
      this.shouldReconnect = true
      
      try {
        this.ws = new WebSocket(this.baseUrl)

        this.ws.onopen = () => {
          console.log('WebSocket connected to download service')
          this.reconnectAttempts = 0
          this.isConnecting = false
          this.onConnectCallbacks.forEach(cb => cb())
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
          this.isConnecting = false
          if (this.reconnectAttempts === 0) {
            console.log('WebSocket connection error - backend may not be running')
          }
          reject(new Error('WebSocket connection failed'))
        }

        this.ws.onclose = (event) => {
          this.isConnecting = false
          this.onDisconnectCallbacks.forEach(cb => cb())
          if (event.code !== 1000) {
            console.log('WebSocket disconnected unexpectedly')
          }
          if (this.shouldReconnect) {
            this.attemptReconnect()
          }
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  private attemptReconnect() {
    if (!this.shouldReconnect) return
    
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = Math.min(this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1), 30000)
      console.log(`WebSocket reconnecting in ${delay}ms (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      setTimeout(() => {
        this.connect().catch(() => {})
      }, delay)
    } else {
      console.log('WebSocket max reconnect attempts reached. Will retry on next page load.')
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

  onConnect(callback: ConnectionCallback) {
    this.onConnectCallbacks.push(callback)
  }

  onDisconnect(callback: ConnectionCallback) {
    this.onDisconnectCallbacks.push(callback)
  }

  disconnect() {
    this.shouldReconnect = false
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

export const useDownloadStore = defineStore('download', () => {
  const tasks = ref<DownloadTask[]>([])
  const total = ref(0)
  const completedCount = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const wsConnected = ref(false)
  const initialized = ref(false)
  const downloadedIds = ref<Set<string>>(new Set())

  let downloadWs: DownloadWebSocket | null = null

  const getWebSocket = (): DownloadWebSocket => {
    if (!downloadWs) {
      downloadWs = new DownloadWebSocket()
      
      downloadWs.onConnect(() => {
        wsConnected.value = true
      })
      
      downloadWs.onDisconnect(() => {
        wsConnected.value = false
      })
    }
    return downloadWs
  }

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
    const ws = getWebSocket()
    if (!wsConnected.value && !ws.isConnected()) {
      try {
        await ws.connect()
        ws.onProgress(async (taskId, progress, status) => {
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
        throw e
      }
    }
  }

  const disconnectWebSocket = () => {
    if (downloadWs) {
      downloadWs.disconnect()
    }
    wsConnected.value = false
  }

  const ensureWebSocketConnection = async () => {
    const ws = getWebSocket()
    if (!wsConnected.value && !ws.isConnected()) {
      try {
        await connectWebSocket()
      } catch (e) {
        setError('WebSocket connection failed - cannot create download task')
        throw new Error('WebSocket connection failed - please ensure the backend is running')
      }
    }
    return ws
  }

  const createTask = async (data: DownloadTaskData) => {
    try {
      setLoading(true)
      setError(null)
      
      const ws = await ensureWebSocketConnection()
      
      const result = await apiService.createDownloadTask(data)
      const existingIndex = tasks.value.findIndex(t => t.id === result.id)
      if (existingIndex >= 0) {
        tasks.value[existingIndex] = result
      } else {
        tasks.value.unshift(result)
      }
      
      if (wsConnected.value || ws.isConnected()) {
        ws.subscribe(result.id)
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

      const ws = await ensureWebSocketConnection()

      const result = await apiService.retryDownloadTask(taskId)
      const existingIndex = tasks.value.findIndex(t => t.id === taskId)
      if (existingIndex >= 0) {
        tasks.value[existingIndex] = result
      }
      
      if (wsConnected.value || ws.isConnected()) {
        ws.subscribe(taskId)
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
