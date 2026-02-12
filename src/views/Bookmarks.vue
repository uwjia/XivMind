<template>
  <div class="bookmarks-page">
    <div class="page-header">
      <h1>My Bookmarks</h1>
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search bookmarks..."
          @keyup.enter="handleSearch"
        />
        <button @click="handleSearch" class="search-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading bookmarks...</p>
    </div>

    <div v-else-if="bookmarks.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="#9E9E9E">
        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
      </svg>
      <p>No bookmarks yet</p>
      <span>Start bookmarking papers you find interesting!</span>
    </div>

    <div v-else class="bookmarks-list">
      <div v-for="bookmark in bookmarks" :key="bookmark.id" class="bookmark-card">
        <div class="bookmark-header">
          <h3 class="bookmark-title" @click="goToDetail(bookmark.paper_id)">{{ bookmark.title }}</h3>
          <button class="remove-btn" @click="removeBookmark(bookmark.paper_id)" title="Remove bookmark">
            <svg viewBox="0 0 24 24" fill="none" stroke="#F44336">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" fill="#FFD700" stroke="#FFD700"/>
            </svg>
          </button>
        </div>
        <p class="bookmark-authors">{{ bookmark.authors?.join(', ') || 'Unknown Authors' }}</p>
        <p class="bookmark-abstract">{{ truncateAbstract(bookmark.abstract) }}</p>
        <div class="bookmark-footer">
          <div class="bookmark-categories">
            <span v-for="cat in (bookmark.categories || []).slice(0, 3)" :key="cat" class="tag" :style="getTagStyle(cat)" :title="getCategoryFullName(cat)">
              {{ getCategoryShortName(cat) }}
            </span>
          </div>
          <div class="bookmark-actions">
            <span class="action-link download-btn" :class="getDownloadStatus(bookmark.paper_id)" @click="handleDownload(bookmark)" :title="getDownloadTitle(bookmark.paper_id)">
              <svg v-if="getDownloadStatus(bookmark.paper_id) === 'downloading'" viewBox="0 0 24 24" fill="none" stroke="#2196F3">
                <circle cx="12" cy="12" r="10" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="10" stroke-width="2" fill="none" stroke-dasharray="62.83" :stroke-dashoffset="62.83 - (62.83 * getDownloadProgress(bookmark.paper_id) / 100)" style="transform: rotate(-90deg); transform-origin: center;"/>
              </svg>
              <svg v-else-if="getDownloadStatus(bookmark.paper_id) === 'completed'" viewBox="0 0 24 24" fill="none" stroke="#4CAF50">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <svg v-else-if="getDownloadStatus(bookmark.paper_id) === 'failed'" viewBox="0 0 24 24" fill="none" stroke="#F44336">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" :stroke="getDownloadStatus(bookmark.paper_id) === 'pending' ? '#FF9800' : '#2196F3'">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7,10 12,15 17,10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              <span v-if="getDownloadStatus(bookmark.paper_id) === 'downloading'">{{ getDownloadProgress(bookmark.paper_id) }}%</span>
              <span v-else-if="getDownloadStatus(bookmark.paper_id) === 'completed'">Downloaded</span>
              <span v-else-if="getDownloadStatus(bookmark.paper_id) === 'failed'">Retry</span>
              <span v-else-if="getDownloadStatus(bookmark.paper_id) === 'pending'">Queued</span>
              <span v-else>Download</span>
            </span>
            <a v-if="bookmark.pdf_url" :href="bookmark.pdf_url" target="_blank" class="action-link">
              <svg viewBox="0 0 24 24" fill="none" stroke="#F44336">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <text x="8" y="16" font-size="6" fill="#F44336" font-weight="bold">PDF</text>
              </svg>
              PDF
            </a>
            <a v-if="bookmark.abs_url" :href="bookmark.abs_url" target="_blank" class="action-link">
              <svg viewBox="0 0 24 24" fill="none" stroke="#4CAF50">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-3 3a5 5 0 0 0 .54 7.54z"/>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l3-3a5 5 0 0 0-.54-7.54z"/>
              </svg>
              arXiv
            </a>
          </div>
        </div>
        <div class="bookmark-date">
          Bookmarked: {{ formatDate(bookmark.created_at) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBookmarkStore } from '../stores/bookmark-store'
import { useDownloadStore } from '../stores/download-store'
import { useToastStore } from '../stores/toast-store'
import { getTagStyle, getCategoryFullName, getCategoryShortName } from '../utils/categoryColors'
import { apiService } from '../services/api'

const router = useRouter()
const route = useRoute()
const bookmarkStore = useBookmarkStore()
const downloadStore = useDownloadStore()
const toastStore = useToastStore()

const bookmarks = computed(() => bookmarkStore.bookmarks)
const loading = ref(true)
const searchQuery = ref('')

const getDownloadStatus = (paperId: string) => {
  const task = downloadStore.tasks.find(t => t.paper_id === paperId)
  return task?.status || 'none'
}

const getDownloadProgress = (paperId: string) => {
  const task = downloadStore.tasks.find(t => t.paper_id === paperId)
  return task?.progress || 0
}

const getDownloadTitle = (paperId: string) => {
  const status = getDownloadStatus(paperId)
  const progress = getDownloadProgress(paperId)
  switch (status) {
    case 'downloading':
      return `Downloading... ${progress}%`
    case 'completed':
      return 'Download completed'
    case 'failed':
      return 'Download failed - click to retry'
    case 'pending':
      return 'Download pending...'
    default:
      return 'Download PDF'
  }
}

const handleDownload = async (bookmark: any) => {
  if (!bookmark.pdf_url || !bookmark.paper_id) {
    toastStore.showError('No PDF URL available')
    return
  }

  const existingTask = downloadStore.tasks.find(t => t.paper_id === bookmark.paper_id)

  if (existingTask) {
    if (existingTask.status === 'failed') {
      try {
        await downloadStore.retryTask(existingTask.id)
        toastStore.showSuccess('Download retry started')
      } catch (error) {
        console.error('Failed to retry download:', error)
        toastStore.showError('Failed to retry download')
      }
    } else if (existingTask.status === 'downloading') {
      toastStore.showInfo('Download already in progress')
    } else if (existingTask.status === 'completed') {
      try {
        await apiService.openDownloadFile(existingTask.id)
      } catch (error) {
        console.error('Failed to open file:', error)
        toastStore.showError('Failed to open file')
      }
    } else {
      toastStore.showInfo('Download already queued')
    }
    return
  }

  try {
    await downloadStore.createTask({
      paper_id: bookmark.paper_id,
      arxiv_id: bookmark.arxiv_id,
      title: bookmark.title,
      pdf_url: bookmark.pdf_url,
    })
    toastStore.showSuccess('Download task added to queue')
  } catch (error) {
    console.error('Failed to create download task:', error)
    toastStore.showError('Failed to create download task')
  }
}

const fetchBookmarks = async () => {
  try {
    loading.value = true
    await bookmarkStore.fetchBookmarks()
    if (downloadStore.tasks.length === 0) {
      await downloadStore.fetchTasks()
    }
  } catch (error) {
    console.error('Failed to fetch bookmarks:', error)
    toastStore.showError('Failed to load bookmarks')
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    await fetchBookmarks()
    return
  }
  try {
    loading.value = true
    await bookmarkStore.searchBookmarks(searchQuery.value)
  } catch (error) {
    console.error('Failed to search bookmarks:', error)
    toastStore.showError('Search failed')
  } finally {
    loading.value = false
  }
}

const removeBookmark = async (paperId: string) => {
  try {
    await bookmarkStore.removeBookmark(paperId)
    toastStore.showSuccess('Bookmark removed')
  } catch (error) {
    console.error('Failed to remove bookmark:', error)
    toastStore.showError('Failed to remove bookmark')
  }
}

const goToDetail = (paperId: string) => {
  router.push({ name: 'PaperDetail', params: { id: paperId } })
}

const truncateAbstract = (abstract: string, maxLength: number = 200) => {
  if (!abstract) return ''
  if (abstract.length <= maxLength) return abstract
  return abstract.substring(0, maxLength) + '...'
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

onMounted(() => {
  fetchBookmarks()
})

watch(
  () => route.path,
  (newPath) => {
    if (newPath === '/bookmarks') {
      fetchBookmarks()
    }
  }
)
</script>

<style scoped>
.bookmarks-page {
  padding: 88px 24px 24px 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.search-box {
  display: flex;
  gap: 8px;
}

.search-box input {
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
  width: 300px;
}

.search-box input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.search-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  background: var(--accent-color);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover {
  opacity: 0.9;
}

.search-btn svg {
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

.bookmarks-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bookmark-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.bookmark-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.bookmark-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.bookmark-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  cursor: pointer;
  flex: 1;
}

.bookmark-title:hover {
  color: var(--accent-color);
}

.remove-btn {
  padding: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background: var(--bg-secondary);
}

.remove-btn svg {
  width: 20px;
  height: 20px;
}

.bookmark-authors {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0 0 12px 0;
}

.bookmark-abstract {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.bookmark-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.bookmark-categories {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 500;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}

.tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.bookmark-actions {
  display: flex;
  gap: 12px;
}

.action-link {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.85rem;
  transition: color 0.3s ease;
}

.action-link:hover {
  color: var(--text-primary);
}

.action-link svg {
  width: 18px;
  height: 18px;
}

.download-btn {
  cursor: pointer;
}

.download-btn.downloading {
  animation: pulse 1.5s infinite;
}

.download-btn.completed {
  color: #4CAF50;
}

.download-btn.failed {
  color: #F44336;
}

.download-btn.pending {
  color: #FF9800;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.bookmark-date {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
  font-size: 0.8rem;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box input {
    width: 100%;
  }

  .bookmark-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
