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
          <div class="header-badges">
            <span class="primary-category" :style="getCategoryStyle(bookmark.primary_category)">{{ bookmark.primary_category || 'CS' }}</span>
            <button class="remove-btn" @click="removeBookmark(bookmark.paper_id)" title="Remove bookmark">
              <svg viewBox="0 0 24 24" fill="none" stroke="#F44336">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" fill="#FFD700" stroke="#FFD700"/>
              </svg>
            </button>
          </div>
        </div>
        
        <p class="bookmark-authors">
          <svg class="author-icon" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="7" r="4" fill="#0b8db4ff"/>
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="#0b8db4ff" stroke-width="2"/>
          </svg>
          <span>{{ bookmark.authors?.join(', ') || 'Unknown Authors' }}</span>
        </p>
        
        <div class="bookmark-abstract">
          <p>
            <svg class="abstract-icon" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="#2196F3" stroke-width="2"/>
              <path d="M2 6h2" stroke="#2196F3" stroke-width="2"/>
              <path d="M2 10h2" stroke="#2196F3" stroke-width="2"/>
              <path d="M2 14h2" stroke="#2196F3" stroke-width="2"/>
              <path d="M2 18h2" stroke="#2196F3" stroke-width="2"/>
              <text x="8" y="16" font-size="6" fill="#2196F3" font-weight="bold">ABS</text>
            </svg>
            <span v-html="getRenderedAbstract(bookmark.abstract)"></span>
          </p>
        </div>
        
        <div v-if="bookmark.comment" class="bookmark-comments">
          <p>
            <svg class="comments-icon" viewBox="0 0 24 24" fill="none">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="#FF9800" stroke-width="2"/>
              <path d="M8 6h.01" stroke="#FF9800" stroke-width="2"/>
              <path d="M12 6h.01" stroke="#FF9800" stroke-width="2"/>
              <path d="M16 6h.01" stroke="#FF9800" stroke-width="2"/>
              <text x="8" y="16" font-size="6" fill="#FF9800" font-weight="bold">COM</text>
            </svg>
            <span v-html="getRenderedComment(bookmark.comment)"></span>
          </p>
        </div>
        
        <div class="bookmark-footer">
          <div class="bookmark-tags">
            <div class="paper-id-section">
              <span class="paper-id">{{ bookmark.arxiv_id || bookmark.paper_id }}</span>
            </div>
            <div class="paper-categories-section">
              <span v-for="cat in (bookmark.categories || []).slice(0, 3)" :key="cat" class="tag" :style="getTagStyle(cat)" :title="getCategoryFullName(cat)">
                {{ getCategoryShortName(cat) }}
              </span>
            </div>
            <div class="paper-published-section">
              <div class="paper-published">Published: {{ formatDate(bookmark.published) }}</div>
              <div v-if="bookmark.updated && bookmark.updated !== bookmark.published" class="paper-updated">Updated: {{ formatDate(bookmark.updated) }}</div>
            </div>
          </div>
          <div class="bookmark-actions">
            <span class="stat-link" @click="openAbsUrl(bookmark.abs_url)" title="Open arXiv page">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-3 3a5 5 0 0 0 .54 7.54z" stroke="#4CAF50" stroke-width="2"/>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l3-3a5 5 0 0 0-.54-7.54z" stroke="#4CAF50" stroke-width="2"/>
              </svg>
            </span>
            <span class="stat-link" @click="openPdfUrl(bookmark.pdf_url)" title="Open PDF">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="#F44336" stroke-width="2"/>
                <path d="M2 6h2" stroke="#F44336" stroke-width="2"/>
                <path d="M2 10h2" stroke="#F44336" stroke-width="2"/>
                <path d="M2 14h2" stroke="#F44336" stroke-width="2"/>
                <path d="M2 18h2" stroke="#F44336" stroke-width="2"/>
                <text x="8" y="16" font-size="6" fill="#F44336" font-weight="bold">PDF</text>
              </svg>
            </span>
            <span class="stat-link download-btn" :class="getDownloadStatus(bookmark.paper_id)" @click="handleDownload(bookmark)" :title="getDownloadTitle(bookmark.paper_id)">
              <svg v-if="getDownloadStatus(bookmark.paper_id) === 'downloading'" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="#2196F3" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="10" stroke="#64B5F6" stroke-width="2" fill="none" stroke-dasharray="62.83" :stroke-dashoffset="62.83 - (62.83 * getDownloadProgress(bookmark.paper_id) / 100)" style="transform: rotate(-90deg); transform-origin: center;"/>
                <text x="12" y="16" font-size="8" fill="#2196F3" text-anchor="middle" font-weight="bold">{{ getDownloadProgress(bookmark.paper_id) }}%</text>
              </svg>
              <svg v-else-if="getDownloadStatus(bookmark.paper_id) === 'completed'" viewBox="0 0 24 24" fill="none">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="#4CAF50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="22 4 12 14.01 9 11.01" stroke="#4CAF50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="getDownloadStatus(bookmark.paper_id) === 'failed'" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="#F44336" stroke-width="2"/>
                <line x1="15" y1="9" x2="9" y2="15" stroke="#F44336" stroke-width="2" stroke-linecap="round"/>
                <line x1="9" y1="9" x2="15" y2="15" stroke="#F44336" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" :stroke="getDownloadStatus(bookmark.paper_id) === 'pending' ? '#FF9800' : '#2196F3'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="7,10 12,15 17,10" :stroke="getDownloadStatus(bookmark.paper_id) === 'pending' ? '#FF9800' : '#2196F3'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="15" x2="12" y2="3" :stroke="getDownloadStatus(bookmark.paper_id) === 'pending' ? '#FF9800' : '#2196F3'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </div>
        </div>
        <div class="bookmark-date">
          Bookmarked: {{ formatDateTime(bookmark.created_at) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import MarkdownIt from 'markdown-it'
import MarkdownItKatex from 'markdown-it-katex'
import 'katex/dist/katex.min.css'
import { useBookmarkStore } from '../stores/bookmark-store'
import { useDownloadStore } from '../stores/download-store'
import { useToastStore } from '../stores/toast-store'
import { getTagStyle, getCategoryFullName, getCategoryShortName, getCategoryColor } from '../utils/categoryColors'
import { apiService } from '../services/api'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
}).use(MarkdownItKatex, {
  throwOnError: false,
  displayMode: false
})

const router = useRouter()
const route = useRoute()
const bookmarkStore = useBookmarkStore()
const downloadStore = useDownloadStore()
const toastStore = useToastStore()

const bookmarks = computed(() => bookmarkStore.bookmarks)
const loading = ref(true)
const searchQuery = ref('')

const getRenderedAbstract = (abstract?: string) => {
  if (!abstract) return '<p>No abstract available</p>'
  return md.render(abstract)
}

const getRenderedComment = (comment?: string) => {
  if (!comment) return ''
  return md.render(comment)
}

const getCategoryStyle = (category?: string) => {
  const color = getCategoryColor(category || 'cs.AI')
  return {
    backgroundColor: color + '20',
    color: color,
    border: `1px solid ${color}40`
  }
}

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

const openAbsUrl = (url: string) => {
  if (url) window.open(url, '_blank')
}

const openPdfUrl = (url: string) => {
  if (url) window.open(url, '_blank')
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

const formatDate = (dateStr?: string) => {
  if (!dateStr) return 'Unknown date'
  try {
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return 'Invalid date'
    const year = date.getUTCFullYear()
    const month = String(date.getUTCMonth() + 1).padStart(2, '0')
    const day = String(date.getUTCDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  } catch {
    return String(dateStr)
  }
}

const formatDateTime = (dateStr?: string) => {
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
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s ease;
}

.bookmark-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.bookmark-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.bookmark-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  cursor: pointer;
  flex: 1;
  line-height: 1.4;
}

.bookmark-title:hover {
  color: var(--accent-color);
}

.header-badges {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.primary-category {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  white-space: nowrap;
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
  font-size: 0.95rem;
  margin: 0 0 16px 0;
}

.author-icon {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  margin-right: 8px;
  float: left;
  margin-top: 2px;
}

.bookmark-authors span {
  display: block;
}

.bookmark-abstract {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 20px;
}

.bookmark-abstract p {
  margin: 0;
}

.bookmark-abstract span {
  display: block;
}

.abstract-icon {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  margin-right: 8px;
  float: left;
  margin-top: 2px;
}

.bookmark-abstract :deep(h1),
.bookmark-abstract :deep(h2),
.bookmark-abstract :deep(h3) {
  margin: 16px 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.bookmark-abstract :deep(ul),
.bookmark-abstract :deep(ol) {
  margin: 8px 0 12px 0;
  padding-left: 24px;
}

.bookmark-abstract :deep(li) {
  margin: 4px 0;
}

.bookmark-abstract :deep(code) {
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.bookmark-abstract :deep(pre) {
  background: var(--bg-secondary);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}

.bookmark-abstract :deep(pre code) {
  background: transparent;
  padding: 0;
  border-radius: 0;
}

.bookmark-comments {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 20px;
}

.bookmark-comments p {
  margin: 0;
}

.bookmark-comments span {
  display: block;
}

.comments-icon {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  margin-right: 8px;
  float: left;
  margin-top: 2px;
}

.bookmark-comments :deep(h1),
.bookmark-comments :deep(h2),
.bookmark-comments :deep(h3) {
  margin: 16px 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.bookmark-comments :deep(ul),
.bookmark-comments :deep(ol) {
  margin: 8px 0 12px 0;
  padding-left: 24px;
}

.bookmark-comments :deep(li) {
  margin: 4px 0;
}

.bookmark-comments :deep(code) {
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.bookmark-comments :deep(pre) {
  background: var(--bg-secondary);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}

.bookmark-comments :deep(pre code) {
  background: transparent;
  padding: 0;
  border-radius: 0;
}

.bookmark-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.bookmark-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  width: 100%;
}

.paper-id-section {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.paper-id {
  font-family: 'Courier New', monospace;
  font-size: 0.7rem;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 8px;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  border: 1px solid transparent;
  color: #00BCD4;
  background-color: rgba(0, 188, 212, 0.1);
  border-color: rgba(0, 188, 212, 0.3);
}

.paper-id:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.paper-categories-section {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  flex-shrink: 1;
}

.paper-published-section {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.paper-published {
  font-family: 'Courier New', monospace;
  font-size: 0.7rem;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 8px;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  border: 1px solid transparent;
  color: #9C27B0;
  background-color: rgba(156, 39, 176, 0.1);
  border-color: rgba(156, 39, 176, 0.3);
  white-space: nowrap;
}

.paper-published:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.paper-updated {
  font-family: 'Courier New', monospace;
  font-size: 0.7rem;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 8px;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  border: 1px solid transparent;
  color: #FF9800;
  background-color: rgba(255, 152, 0, 0.1);
  border-color: rgba(255, 152, 0, 0.3);
  white-space: nowrap;
}

.paper-updated:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
  flex-shrink: 0;
}

.stat-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.stat-link:hover {
  background: var(--bg-secondary);
  transform: scale(1.1);
}

.stat-link svg {
  width: 18px;
  height: 18px;
}

.download-btn {
  cursor: pointer;
}

.download-btn.downloading {
  animation: pulse 1.5s infinite;
}

.download-btn.completed svg {
  color: #4CAF50;
}

.download-btn.failed svg {
  color: #F44336;
}

.download-btn.pending svg {
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
  
  .bookmark-tags {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
