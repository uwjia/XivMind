<template>
  <div v-if="paper" class="paper-card-container">
    <div class="paper-card" :style="cardStyle">
      <div class="paper-title-section">
        <h3 class="paper-title" @click="goToDetail">{{ paper.title || 'Untitled' }}</h3>
        <span class="paper-primary-category" :style="categoryStyle">{{ paper.primaryCategory || paper.category || 'CS' }}</span>
        <span class="paper-index" :style="indexStyle">{{ index || 'N/A' }}</span>
      </div>
      <p class="paper-authors">
        <svg class="author-icon" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="7" r="4" fill="#0b8db4ff"/>
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="#0b8db4ff" stroke-width="2"/>
        </svg>
        <span>{{ paper.authors?.join(', ') || 'Unknown Authors' }}</span>
      </p>
      <div class="paper-abstract">
        <p>
          <svg class="abstract-icon" viewBox="0 0 24 24" fill="none">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="#2196F3" stroke-width="2"/>
            <path d="M2 6h2" stroke="#2196F3" stroke-width="2"/>
            <path d="M2 10h2" stroke="#2196F3" stroke-width="2"/>
            <path d="M2 14h2" stroke="#2196F3" stroke-width="2"/>
            <path d="M2 18h2" stroke="#2196F3" stroke-width="2"/>
            <text x="8" y="16" font-size="6" fill="#2196F3" font-weight="bold">ABS</text>
          </svg>
          <span v-html="renderedAbstract"></span>
        </p>
      </div>
      <div v-if="paper.comment" class="paper-comments">
        <p>
          <svg class="comments-icon" viewBox="0 0 24 24" fill="none">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="#FF9800" stroke-width="2"/>
            <path d="M8 6h.01" stroke="#FF9800" stroke-width="2"/>
            <path d="M12 6h.01" stroke="#FF9800" stroke-width="2"/>
            <path d="M16 6h.01" stroke="#FF9800" stroke-width="2"/>
            <text x="8" y="16" font-size="6" fill="#FF9800" font-weight="bold">COM</text>
          </svg>
          <span v-html="renderedComments"></span>
        </p>
      </div>
      <div class="paper-footer">
        <div class="paper-tags">
          <div class="paper-id-section">
            <span class="paper-id" :style="idStyle">{{ paper.id || 'N/A' }}</span>
          </div>
          <div class="paper-categories-section">
            <span v-for="cat in (paper.categories || []).slice(0, 3)" :key="cat" class="tag" :style="getTagStyle(cat)" :title="getCategoryFullName(cat)">{{ getCategoryShortName(cat) }}</span>
          </div>
          <div class="paper-published-section">
            <div class="paper-published">v1 {{ formatDate(paper.published) }}</div>
            <div v-if="getVersionFromId() !== 1" class="paper-updated">v{{ getVersionFromId() }} {{ formatDate(paper.updated) }}</div>
          </div>
        </div>
        <div class="paper-stats">
          <span class="stat-link" @click.stop="openAbsUrl" :title="'Open arXiv page'">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-3 3a5 5 0 0 0 .54 7.54z" stroke="#4CAF50" stroke-width="2"/>
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l3-3a5 5 0 0 0-.54-7.54z" stroke="#4CAF50" stroke-width="2"/>
            </svg>
          </span>
          <span class="stat-link" @click.stop="openPdfUrl" :title="'Open PDF'">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="#F44336" stroke-width="2"/>
              <path d="M2 6h2" stroke="#F44336" stroke-width="2"/>
              <path d="M2 10h2" stroke="#F44336" stroke-width="2"/>
              <path d="M2 14h2" stroke="#F44336" stroke-width="2"/>
              <path d="M2 18h2" stroke="#F44336" stroke-width="2"/>
              <text x="8" y="16" font-size="6" fill="#F44336" font-weight="bold">PDF</text>
            </svg>
          </span>
          <span class="stat-link download-btn" @click.stop="downloadPdf" :title="downloadTitle" :class="downloadStatus">
            <svg v-if="downloadStatus === 'downloading'" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="#2196F3" stroke-width="2" fill="none"/>
              <circle cx="12" cy="12" r="10" stroke="#64B5F6" stroke-width="2" fill="none" stroke-dasharray="62.83" :stroke-dashoffset="62.83 - (62.83 * downloadProgress / 100)" style="transform: rotate(-90deg); transform-origin: center;"/>
              <text x="12" y="16" font-size="8" fill="#2196F3" text-anchor="middle" font-weight="bold">{{ downloadProgress }}%</text>
            </svg>
            <svg v-else-if="downloadStatus === 'completed'" viewBox="0 0 24 24" fill="none">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="#4CAF50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="22 4 12 14.01 9 11.01" stroke="#4CAF50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else-if="downloadStatus === 'failed'" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="#F44336" stroke-width="2"/>
              <line x1="15" y1="9" x2="9" y2="15" stroke="#F44336" stroke-width="2" stroke-linecap="round"/>
              <line x1="9" y1="9" x2="15" y2="15" stroke="#F44336" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" :stroke="downloadStatus === 'pending' ? '#FF9800' : '#2196F3'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="7,10 12,15 17,10" :stroke="downloadStatus === 'pending' ? '#FF9800' : '#2196F3'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="12" y1="15" x2="12" y2="3" :stroke="downloadStatus === 'pending' ? '#FF9800' : '#2196F3'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="stat-link bookmark-btn" @click.stop="toggleBookmark" :title="isBookmarked ? 'Remove bookmark' : 'Add bookmark'" :class="{ bookmarked: isBookmarked }">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" 
                    :stroke="isBookmarked ? '#FFD700' : '#FF9800'" 
                    stroke-width="2" 
                    stroke-linecap="round" 
                    stroke-linejoin="round"
                    :fill="isBookmarked ? '#FFD700' : 'none'"/>
            </svg>
          </span>
          <span class="stat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            {{ paper.downloads || paper.views || 0 }}
          </span>
          <span class="stat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            {{ paper.citations || 0 }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'
import MarkdownItKatex from 'markdown-it-katex'
import 'katex/dist/katex.min.css'
import { getCategoryColor, getTagStyle, categories } from '../utils/categoryColors'
import { useBookmarkStore } from '../stores/bookmark-store'
import { useDownloadStore } from '../stores/download-store'
import { useToastStore } from '../stores/toast-store'
import { apiService } from '../services/api'
import type { Paper } from '../types'

const props = defineProps<{
  paper: Paper
  index?: number
}>()

const router = useRouter()
const bookmarkStore = useBookmarkStore()
const downloadStore = useDownloadStore()
const toastStore = useToastStore()
const isBookmarked = ref(false)

const downloadStatus = computed(() => {
  if (!props.paper?.id) return 'none'
  const task = downloadStore.tasks.find(t => t.paper_id === props.paper.id)
  return task?.status || 'none'
})

const downloadProgress = computed(() => {
  if (!props.paper?.id) return 0
  const task = downloadStore.tasks.find(t => t.paper_id === props.paper.id)
  return task?.progress || 0
})

const downloadTitle = computed(() => {
  switch (downloadStatus.value) {
    case 'downloading':
      return `Downloading... ${downloadProgress.value}%`
    case 'completed':
      return 'Download completed'
    case 'failed':
      return 'Download failed - click to retry'
    case 'pending':
      return 'Download pending...'
    default:
      return 'Download PDF'
  }
})

// 初始化markdown-it实例
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
}).use(MarkdownItKatex, {
  throwOnError: false,
  displayMode: false
})

const renderedAbstract = computed(() => {
  if (!props.paper?.abstract) return '<p>No abstract available</p>'
  return md.render(props.paper.abstract)
})

const renderedComments = computed(() => {
  if (!props.paper?.comment) return ''
  return md.render(props.paper.comment)
})

const idStyle = computed(() => {
  // const color = getIdColor(props.paper?.id)
  const color = '#00BCD4'
  return {
    backgroundColor: color + '15',
    color: color,
    border: `1px solid ${color}30`
  }
})

const cardStyle = computed(() => {
  return {
    transformStyle: 'preserve-3d' as const,
    transition: 'all 0.3s ease'
  }
})

const categoryStyle = computed(() => {
  const color = getCategoryColor(props.paper?.primaryCategory || props.paper?.category || 'cs.AI')
  return {
    backgroundColor: color + '20',
    color: color,
    border: `1px solid ${color}40`
  }
})

const indexStyle = computed(() => {
  const color = '#2dadf7'
  return {
    backgroundColor: color + '20',
    color: color,
    border: `1px solid ${color}40`
  }
})

const goToDetail = () => {
  if (!props.paper?.id) {
    console.warn('Paper has no ID, cannot navigate to detail')
    return
  }
  router.push({ name: 'PaperDetail', params: { id: props.paper.id } })
}

const openAbsUrl = () => {
  if (!props.paper?.absUrl) {
    console.warn('Paper has no absUrl')
    return
  }
  window.open(props.paper.absUrl, '_blank')
}

const openPdfUrl = () => {
  if (!props.paper?.pdfUrl) {
    console.warn('Paper has no pdfUrl')
    return
  }
  window.open(props.paper.pdfUrl, '_blank')
}

const downloadPdf = async () => {
  if (!props.paper?.pdfUrl || !props.paper?.id) {
    console.warn('Paper has no pdfUrl or id')
    return
  }
  
  const existingTask = downloadStore.tasks.find(t => t.paper_id === props.paper.id)
  
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
      paper_id: props.paper.id,
      arxiv_id: props.paper.arxivId,
      title: props.paper.title,
      pdf_url: props.paper.pdfUrl,
    })
    toastStore.showSuccess('Download task added to queue')
  } catch (error) {
    console.error('Failed to create download task:', error)
    toastStore.showError('Failed to create download task')
  }
}

const toggleBookmark = async () => {
  if (!props.paper?.id) {
    console.warn('Paper has no id')
    return
  }
  try {
    const result = await bookmarkStore.toggleBookmark({
      paper_id: props.paper.id,
      arxiv_id: props.paper.arxivId,
      title: props.paper.title,
      authors: props.paper.authors,
      abstract: props.paper.abstract,
      comment: props.paper.comment,
      primary_category: props.paper.primaryCategory,
      categories: props.paper.categories,
      pdf_url: props.paper.pdfUrl,
      abs_url: props.paper.absUrl,
      published: props.paper.published?.toString(),
      updated: props.paper.updated?.toString(),
    })
    isBookmarked.value = result
    toastStore.showSuccess(result ? 'Added to bookmarks' : 'Removed from bookmarks')
  } catch (error) {
    console.error('Failed to toggle bookmark:', error)
    toastStore.showError('Failed to update bookmark')
  }
}

onMounted(async () => {
  if (props.paper?.id) {
    isBookmarked.value = await bookmarkStore.checkBookmark(props.paper.id)
  }
  if (downloadStore.tasks.length === 0) {
    await downloadStore.fetchTasks()
  }
})

const formatDate = (dateStr: string | Date) => {
  if (!dateStr) return 'Unknown date'
  
  try {
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return 'Invalid date'
    
    const year = date.getUTCFullYear()
    const month = String(date.getUTCMonth() + 1).padStart(2, '0')
    const day = String(date.getUTCDate()).padStart(2, '0')
    const hours = String(date.getUTCHours()).padStart(2, '0')
    const minutes = String(date.getUTCMinutes()).padStart(2, '0')
    const seconds = String(date.getUTCSeconds()).padStart(2, '0')
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  } catch (err) {
    console.error('Error formatting date:', err)
    return String(dateStr)
  }
}

const getCategoryShortName = (category: string) => {
  if (!category) return 'CS'
  const parts = category.split('.')
  return parts[parts.length - 1]?.toUpperCase() || category.toUpperCase()
}

const getCategoryFullName = (category: string) => {
  if (!category) return 'Unknown Category'
  const categoryData = categories.find(cat => cat.id === category)
  return categoryData?.name || category
}

const getVersionFromId = () => {
  const pdfUrl = props.paper.pdfUrl || ''
  const versionMatch = pdfUrl.match(/v(\d+)$/)
  if (versionMatch && versionMatch[1]) {
    return parseInt(versionMatch[1])
  }
  const arxivId = props.paper.id || ''
  const idVersionMatch = arxivId.match(/v(\d+)$/)
  if (idVersionMatch && idVersionMatch[1]) {
    return parseInt(idVersionMatch[1])
  }
  return 1
}
</script>

<style scoped>
.paper-card-container {
  perspective: 1000px;
  margin: 0px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.paper-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  cursor: default;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  transform-style: preserve-3d;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  width: 100%;
  min-height: 420px;
  height: auto;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.paper-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
  pointer-events: none;
}

.paper-card:hover {
  box-shadow: 
    0 12px 36px rgba(0, 0, 0, 0.12),
    0 4px 12px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.paper-header {
  margin-bottom: 12px;
  z-index: 1;
  position: relative;
}

.paper-id-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  max-width: 100%;
  overflow: hidden;
}

.paper-index {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  white-space: nowrap;
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
}

.paper-id:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.paper-categories {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  max-width: 100%;
  overflow: hidden;
}

.category-tag {
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 500;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}

.category-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.paper-title-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.paper-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
  z-index: 1;
  position: relative;
  flex: 1;
  min-width: 0;
  cursor: pointer;
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}

.paper-title:hover {
  color: var(--accent-color);
}

.paper-primary-category {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  white-space: nowrap;
}

.paper-authors {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 16px;
  z-index: 1;
  position: relative;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.author-icon {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  margin-right: 8px;
  float: left;
  margin-top: 2px;
}

.paper-abstract {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 20px;
  z-index: 1;
  position: relative;
  flex: 1;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.paper-abstract p {
  margin: 0;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.paper-abstract span {
  display: block;
}

.paper-authors span {
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

.paper-abstract h1, .paper-abstract h2, .paper-abstract h3 {
  margin: 16px 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.paper-abstract ul, .paper-abstract ol {
  margin: 8px 0 12px 0;
  padding-left: 24px;
}

.paper-abstract li {
  margin: 4px 0;
}

.paper-abstract code {
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  word-break: break-all;
}

.paper-abstract pre {
  background: var(--bg-secondary);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
  max-width: 100%;
  box-sizing: border-box;
}

.paper-abstract pre code {
  background: transparent;
  padding: 0;
  border-radius: 0;
}

.paper-abstract a,
.paper-comments a {
  word-break: break-all;
  overflow-wrap: break-word;
}

.paper-comments {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 20px;
  z-index: 1;
  position: relative;
  flex: 1;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.paper-comments p {
  margin: 0;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.paper-comments span {
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

.paper-comments h1, .paper-comments h2, .paper-comments h3 {
  margin: 16px 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.paper-comments ul, .paper-comments ol {
  margin: 8px 0 12px 0;
  padding-left: 24px;
}

.paper-comments li {
  margin: 4px 0;
}

.paper-comments code {
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  word-break: break-all;
}

.paper-comments pre {
  background: var(--bg-secondary);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
  max-width: 100%;
  box-sizing: border-box;
}

.paper-comments pre code {
  background: transparent;
  padding: 0;
  border-radius: 0;
}

.paper-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  z-index: 1;
  position: relative;
  flex-shrink: 0;
  overflow: hidden;
}

.paper-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
}

.paper-id-section {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.paper-categories-section {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  flex-shrink: 1;
  max-width: 100%;
  overflow: hidden;
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

.paper-stats {
  display: flex;
  gap: 20px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-muted);
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.stat:hover {
  color: var(--text-primary);
}

.stat svg {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
}

.stat:hover svg {
  transform: scale(1.1);
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

.bookmark-btn svg {
  transition: all 0.3s ease;
}

.bookmark-btn:hover svg {
  transform: scale(1.1);
}

.bookmark-btn.bookmarked {
  animation: bookmarkPop 0.3s ease;
}

@keyframes bookmarkPop {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

@media (max-width: 768px) {
  .paper-card-container {
    margin: 12px;
  }
  
  .paper-card {
    padding: 20px;
    min-height: 380px;
    height: auto;
  }

  .paper-title {
    font-size: 1.2rem;
  }

  .paper-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .paper-card:hover {
    transform: translateY(-6px);
  }
}
</style>
