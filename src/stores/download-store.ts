import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService, type DownloadTask, type DownloadTaskData } from '../services/api'

type ProgressCallback = (taskId: string, progress: number, status: string) => void

class DownloadWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private progressCallbacks: ProgressCallback[] = []
  private baseUrl: string

  constructor() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    this.baseUrl = `${protocol}//localhost:8000/api/downloads/ws`
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

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
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
  const loading = ref(false)
  const error = ref<string | null>(null)
  const wsConnected = ref(false)

  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const setError = (value: string | null) => {
    error.value = value
  }

  const connectWebSocket = async () => {
    if (!wsConnected.value) {
      try {
        await downloadWs.connect()
        wsConnected.value = true
        
        downloadWs.onProgress(async (taskId, progress, status) => {
          const task = tasks.value.find(t => t.id === taskId)
          if (task) {
            task.progress = progress
            task.status = status as 'pending' | 'downloading' | 'completed' | 'failed'
            
            if (status === 'completed' || status === 'failed') {
              try {
                const updatedTask = await apiService.getDownloadTask(taskId)
                const existingIndex = tasks.value.findIndex(t => t.id === taskId)
                if (existingIndex >= 0) {
                  tasks.value[existingIndex] = updatedTask
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

  const fetchTasks = async (limit: number = 100, offset: number = 0) => {
    try {
      setLoading(true)
      setError(null)
      const result = await apiService.getDownloadTasks(limit, offset)
      tasks.value = result.items
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
      await apiService.deleteDownloadTask(taskId)
      tasks.value = tasks.value.filter(t => t.id !== taskId)
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

  return {
    tasks,
    loading,
    error,
    wsConnected,
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
  }
})
