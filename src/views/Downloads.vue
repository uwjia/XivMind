<template>
  <div class="downloads-page">
    <div class="page-header">
      <h1>Download Manager</h1>
      <div class="header-actions">
        <span v-if="wsConnected" class="ws-status connected">
          <span class="ws-dot"></span>
          Real-time
        </span>
        <span v-else class="ws-status disconnected">
          <span class="ws-dot"></span>
          Polling
        </span>
        <button @click="refreshTasks" class="refresh-btn" :disabled="loading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M23 4v6h-6"/>
            <path d="M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <div v-if="loading && tasks.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>Loading download tasks...</p>
    </div>

    <div v-else-if="tasks.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="#9E9E9E">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7,10 12,15 17,10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
      </svg>
      <p>No download tasks</p>
      <span>Click the download button on any paper to start downloading!</span>
    </div>

    <div v-else class="downloads-list">
      <div v-for="task in tasks" :key="task.id" class="download-card" :class="task.status">
        <div class="download-header">
          <h3 class="download-title">{{ task.title }}</h3>
          <span class="status-badge" :class="task.status">
            {{ getStatusLabel(task.status) }}
          </span>
        </div>

        <div class="download-info">
          <span class="paper-id">{{ task.paper_id }}</span>
          <span class="download-time">{{ formatDate(task.created_at) }}</span>
        </div>

        <div v-if="task.status === 'downloading'" class="progress-bar">
          <div class="progress-fill" :style="{ width: `${task.progress}%` }"></div>
          <span class="progress-text">{{ task.progress }}%</span>
        </div>

        <div v-if="task.status === 'failed' && task.error_message" class="error-message">
          <svg viewBox="0 0 24 24" fill="none" stroke="#F44336">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          {{ task.error_message }}
        </div>

        <div v-if="task.status === 'completed' && task.file_path" class="file-path">
          <svg viewBox="0 0 24 24" fill="none" stroke="#4CAF50">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          Saved to: {{ task.file_path }}
          <span v-if="task.file_size" class="file-size">({{ formatFileSize(task.file_size) }})</span>
        </div>

        <div class="download-actions">
          <button
            v-if="task.status === 'downloading'"
            @click="cancelTask(task.id)"
            class="action-btn cancel"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            Cancel
          </button>
          <button
            v-if="task.status === 'failed'"
            @click="retryTask(task.id)"
            class="action-btn retry"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M23 4v6h-6"/>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
            Retry
          </button>
          <button
            v-if="task.status === 'completed' && task.file_path"
            @click="openFile(task.id)"
            class="action-btn open"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            Open File
          </button>
          <button
            @click="deleteTask(task.id)"
            class="action-btn delete"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            Delete
          </button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :visible="showDeleteConfirm"
      title="Delete Download Task"
      :message="deleteConfirmMessage"
      type="danger"
      confirmText="Delete"
      cancelText="Cancel"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { useDownloadStore } from '../stores/download-store'
import { useToastStore } from '../stores/toast-store'
import { apiService } from '../services/api'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const downloadStore = useDownloadStore()
const toastStore = useToastStore()

const tasks = computed(() => downloadStore.tasks)
const loading = computed(() => downloadStore.loading)
const wsConnected = computed(() => downloadStore.wsConnected)
let refreshInterval: number | null = null

const showDeleteConfirm = ref(false)
const taskToDelete = ref<string | null>(null)
const taskToDeleteTitle = ref<string>('')

const deleteConfirmMessage = computed(() => {
  if (taskToDeleteTitle.value) {
    return `Are you sure you want to delete the download task for "${taskToDeleteTitle.value}"? This action cannot be undone.`
  }
  return 'Are you sure you want to delete this download task? This action cannot be undone.'
})

const fetchTasks = async () => {
  try {
    await downloadStore.fetchTasks()
  } catch (error) {
    console.error('Failed to fetch download tasks:', error)
    toastStore.showError('Failed to load download tasks')
  }
}

const refreshTasks = () => {
  fetchTasks()
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

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: 'Pending',
    downloading: 'Downloading',
    completed: 'Completed',
    failed: 'Failed'
  }
  return labels[status] || status
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return 'Unknown'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

const formatFileSize = (bytes: number) => {
  if (!bytes || bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(i > 0 ? 1 : 0)} ${units[i]}`
}

onMounted(async () => {
  await downloadStore.connectWebSocket()
  await fetchTasks()
  
  refreshInterval = window.setInterval(() => {
    if (!wsConnected.value) {
      const hasActiveTasks = tasks.value.some(t => t.status === 'pending' || t.status === 'downloading')
      if (hasActiveTasks) {
        fetchTasks()
      }
    }
  }, 3000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  downloadStore.disconnectWebSocket()
})
</script>

<style scoped>
.downloads-page {
  padding: 88px 24px 24px 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ws-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  padding: 4px 12px;
  border-radius: 12px;
}

.ws-status.connected {
  background: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
}

.ws-status.disconnected {
  background: rgba(158, 158, 158, 0.1);
  color: #9E9E9E;
}

.ws-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn svg {
  width: 18px;
  height: 18px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px;
  color: var(--text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px;
  color: var(--text-muted);
}

.empty-state svg {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 1.25rem;
  margin: 0 0 8px 0;
}

.empty-state span {
  font-size: 0.9rem;
}

.downloads-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.download-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.download-card.downloading {
  border-color: #2196F3;
}

.download-card.completed {
  border-color: #4CAF50;
}

.download-card.failed {
  border-color: #F44336;
}

.download-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.download-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.pending {
  background: rgba(158, 158, 158, 0.2);
  color: #9E9E9E;
}

.status-badge.downloading {
  background: rgba(33, 150, 243, 0.2);
  color: #2196F3;
}

.status-badge.completed {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.status-badge.failed {
  background: rgba(244, 67, 54, 0.2);
  color: #F44336;
}

.download-info {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.progress-bar {
  position: relative;
  height: 24px;
  background: var(--bg-secondary);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2196F3, #64B5F6);
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-primary);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(244, 67, 54, 0.1);
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 0.85rem;
  color: #F44336;
}

.error-message svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.file-path {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 0.85rem;
  color: #4CAF50;
  word-break: break-all;
}

.file-path svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.file-size {
  margin-left: 8px;
  opacity: 0.8;
  font-size: 0.8rem;
}

.download-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s ease;
}

.action-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.action-btn.retry:hover {
  border-color: #FF9800;
  color: #FF9800;
}

.action-btn.cancel:hover {
  border-color: #F44336;
  color: #F44336;
}

.action-btn.open:hover {
  border-color: #4CAF50;
  color: #4CAF50;
}

.action-btn.delete:hover {
  border-color: #F44336;
  color: #F44336;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .header-actions {
    justify-content: space-between;
  }

  .download-header {
    flex-direction: column;
  }

  .download-actions {
    flex-direction: column;
  }

  .action-btn {
    justify-content: center;
  }
}
</style>
