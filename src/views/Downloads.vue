<template>
  <div class="downloads-page">
    <div class="page-header">
      <h1>Download Manager <span v-if="completedCount > 0" class="total-count">(total {{ completedCount }} completed)</span></h1>
      <div class="header-actions">
        <div class="filter-dropdown">
          <select v-model="filterMode" @change="setFilterMode(filterMode)" class="filter-select">
            <option value="all">All Tasks</option>
            <option value="incomplete">Incomplete</option>
            <option value="missing">Missing Files</option>
          </select>
        </div>
        <div class="view-toggle">
          <button 
            class="toggle-btn" 
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
            title="List View"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="8" y1="6" x2="21" y2="6" stroke-width="2"/>
              <line x1="8" y1="12" x2="21" y2="12" stroke-width="2"/>
              <line x1="8" y1="18" x2="21" y2="18" stroke-width="2"/>
              <line x1="3" y1="6" x2="3.01" y2="6" stroke-width="2"/>
              <line x1="3" y1="12" x2="3.01" y2="12" stroke-width="2"/>
              <line x1="3" y1="18" x2="3.01" y2="18" stroke-width="2"/>
            </svg>
          </button>
          <button 
            class="toggle-btn" 
            :class="{ active: viewMode === 'desktop' }"
            @click="viewMode = 'desktop'"
            title="Desktop View"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2" stroke-width="2"/>
              <line x1="8" y1="21" x2="16" y2="21" stroke-width="2"/>
              <line x1="12" y1="17" x2="12" y2="21" stroke-width="2"/>
            </svg>
          </button>
        </div>
        <span v-if="wsConnected" class="ws-status connected">
          <span class="ws-dot"></span>
          Real-time
        </span>
        <span v-else class="ws-status disconnected">
          <span class="ws-dot"></span>
          Polling
        </span>
        <button @click="syncLocalFiles" class="sync-btn" :disabled="loading" title="Sync local PDF files">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="17 8 12 3 7 8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="3" x2="12" y2="15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button @click="refreshTasks" class="refresh-btn" :disabled="loading" title="Refresh download tasks">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M23 4v6h-6"/>
            <path d="M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading download tasks...</p>
    </div>

    <div v-else-if="tasks.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="#9E9E9E">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7,10 12,15 17,10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
      </svg>
      <p v-if="filterMode === 'incomplete'">No incomplete tasks</p>
      <p v-else-if="filterMode === 'missing'">No missing files</p>
      <p v-else>No download tasks</p>
      <span v-if="filterMode === 'all'">Click the download button on any paper to start downloading!</span>
    </div>

    <template v-else>
      <DesktopView v-if="viewMode === 'desktop'" :tasks="tasks" />
      
      <template v-else>
      <div class="downloads-list">
        <div v-for="task in tasks" :key="task.id" class="download-card" :class="task.status">
          <div class="download-header">
            <h3 class="download-title" @click="goToDetail(task.paper_id)">{{ task.title }}</h3>
            <span class="status-badge" :class="task.status">
              {{ getDownloadStatusLabel(task.status) }}
            </span>
          </div>

          <div class="download-info">
            <span class="paper-id">{{ task.paper_id }}</span>
            <span class="download-time">{{ formatDateTime(task.created_at) }}</span>
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
            <svg viewBox="0 0 24 24" fill="none" stroke="#00BCD4">
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
              v-if="task.status === 'completed' && task.file_path"
              @click="openReader(task.paper_id)"
              class="action-btn read"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" stroke-width="2"/>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" stroke-width="2"/>
              </svg>
              Read
            </button>
            <button
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

      <div v-if="!loading && tasks.length > 0 && totalPages > 1" class="pagination">
        <button
          class="pagination-btn"
          @click="goToFirstPage"
          :disabled="currentPage === 0"
        >
          First
        </button>
        <button
          class="pagination-btn"
          @click="goToPreviousPage"
          :disabled="currentPage === 0"
        >
          Previous
        </button>
        <span class="pagination-info">
          Page {{ currentPage + 1 }} of {{ totalPages }}
        </span>
        <button
          class="pagination-btn"
          @click="goToNextPage"
          :disabled="currentPage >= totalPages - 1"
        >
          Next
        </button>
        <div class="pagination-jump">
          <input
            type="number"
            v-model="jumpPageInput"
            :placeholder="`1-${totalPages}`"
            min="1"
            :max="totalPages"
            @keyup.enter="handleGoToPage"
          />
          <button class="pagination-btn" @click="handleGoToPage">Go</button>
        </div>
      </div>
      </template>
    </template>

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

    <ScrollTopButton />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useDownloadActions } from '@/composables/useDownloadActions'
import { useDateFormatter } from '@/composables/useDateFormatter'
import { formatFileSize, getDownloadStatusLabel } from '@/utils/format'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import DesktopView from '@/components/desktop/DesktopView.vue'
import ScrollTopButton from '@/components/ScrollTopButton.vue'

const STORAGE_KEY = 'xivmind-downloads-view-mode'

const getSavedViewMode = (): 'list' | 'desktop' => {
  const saved = localStorage.getItem(STORAGE_KEY)
  return (saved === 'list' || saved === 'desktop') ? saved : 'list'
}

const viewMode = ref<'list' | 'desktop'>(getSavedViewMode())

watch(viewMode, (newMode) => {
  localStorage.setItem(STORAGE_KEY, newMode)
})

const {
  tasks,
  completedCount,
  loading,
  wsConnected,
  currentPage,
  totalPages,
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
  handleGoToPage,
  syncLocalFiles,
  setFilterMode,
} = useDownloadActions()

const { formatDateTime } = useDateFormatter()

onMounted(() => {
  fetchTasks()
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
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.total-count {
  font-size: 1rem;
  font-weight: 400;
  color: var(--text-muted);
  margin-left: 8px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filter-dropdown {
  display: flex;
}

.filter-select {
  padding: 8px 32px 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  transition: all 0.2s;
}

.filter-select:hover {
  border-color: var(--accent-color);
}

.filter-select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(var(--accent-color-rgb), 0.1);
}

.view-toggle {
  display: flex;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 4px;
  gap: 4px;
}

.toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn:hover {
  color: var(--text-primary);
  background: var(--bg-primary);
}

.toggle-btn.active {
  background: var(--bg-primary);
  color: var(--accent-color);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toggle-btn svg {
  width: 18px;
  height: 18px;
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
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
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

.sync-btn {
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

.sync-btn:hover:not(:disabled) {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.sync-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sync-btn svg {
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
  border-color: #00BCD4;
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
  cursor: pointer;
  transition: color 0.3s ease;
}

.download-title:hover {
  color: var(--accent-color);
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
  background: rgba(0, 188, 212, 0.2);
  color: #00BCD4;
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
  background: rgba(0, 188, 212, 0.1);
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 0.85rem;
  color: #00BCD4;
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
  border-color: #00BCD4;
  color: #00BCD4;
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

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
  padding: 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.9rem;
  color: var(--text-muted);
  min-width: 120px;
  text-align: center;
}

.pagination-jump {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-jump input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  text-align: center;
}

.pagination-jump input::-webkit-outer-spin-button,
.pagination-jump input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.pagination-jump input[type=number] {
  -moz-appearance: textfield;
}
</style>
