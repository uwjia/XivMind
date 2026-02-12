<template>
  <div class="paper-detail">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading paper...</p>
    </div>
    <div v-else-if="error" class="error-state">
      <div class="error-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>
      <h3>Error Loading Paper</h3>
      <p>{{ error }}</p>
      <button @click="goBack" class="retry-button">Go Back</button>
    </div>
    <div v-else-if="!paper" class="loading-state">
      <div class="spinner"></div>
      <p>Loading paper...</p>
    </div>
    <div v-else class="detail-container">
      <div class="main-content">
        <div class="paper-header">
          <div class="header-info">
            <span class="paper-id">{{ paper.id }}</span>
            <span class="paper-category">{{ paper.category }}</span>
            <span class="paper-date">{{ formatDate(paper.date) }}</span>
          </div>
          <button @click="goBack" class="back-button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Back
          </button>
        </div>

        <h1 class="paper-title">{{ paper.title }}</h1>

        <div class="paper-authors">
          <span v-for="(author, index) in paper.authors" :key="index" class="author">
            {{ author }}{{ index < paper.authors.length - 1 ? ', ' : '' }}
          </span>
        </div>

        <div class="paper-stats">
          <div class="stat-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            <span>{{ paper?.downloads || 0 }} downloads</span>
          </div>
          <div class="stat-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="#10b981">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            <span>{{ paper?.citations || 0 }} citations</span>
          </div>
        </div>

        <div class="paper-actions">
          <a :href="paper.pdfUrl" target="_blank" class="action-button primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            View PDF
          </a>
          <a :href="paper.absUrl" target="_blank" class="action-button secondary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            View on arXiv
          </a>
        </div>

        <div class="paper-tags">
          <span v-for="cat in paper.categories" :key="cat" class="tag" :style="getTagStyle(cat)" :title="getCategoryFullName(cat)">{{ cat }}</span>
        </div>

        <div v-if="paper.comment" class="paper-comments">
          <h2>Comments</h2>
          <div v-html="renderedComment" class="comments-content"></div>
        </div>

        <div class="paper-abstract">
          <h2>Abstract</h2>
          <div v-html="renderedAbstract" class="abstract-content"></div>
        </div>

        <div class="ai-insights">
          <h2>
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--accent-color)">
              <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            AI-Powered Insights
          </h2>
          <div class="insight-card">
            <h3>Key Contributions</h3>
            <ul>
              <li>Novel approach to handling long-context problems in vision-language models</li>
              <li>7-20x compression ratio while maintaining high OCR accuracy</li>
              <li>State-of-the-art performance with significantly fewer visual tokens</li>
            </ul>
          </div>
          <div class="insight-card">
            <h3>Related Papers</h3>
            <div class="related-papers">
              <div v-for="related in relatedPapers" :key="related.id" class="related-paper" @click="goToPaper(related.id)">
                <span class="related-id">{{ related.id }}</span>
                <span class="related-title">{{ related.title }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <aside class="sidebar">
        <div class="sidebar-section">
          <h3>Quick Actions</h3>
          <div class="action-list">
            <button class="sidebar-action" :class="{ active: isBookmarked }" @click="toggleBookmark">
              <svg viewBox="0 0 24 24" fill="none" :stroke="isBookmarked ? '#FFD700' : '#f59e0b'">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" :fill="isBookmarked ? '#FFD700' : 'none'"/>
              </svg>
              {{ isBookmarked ? 'Bookmarked' : 'Bookmark' }}
            </button>
            <button class="sidebar-action" :class="downloadStatus" @click="downloadPdf">
              <svg v-if="downloadStatus === 'downloading'" viewBox="0 0 24 24" fill="none" stroke="#2196F3">
                <circle cx="12" cy="12" r="10" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="10" stroke-width="2" fill="none" stroke-dasharray="62.83" :stroke-dashoffset="62.83 - (62.83 * downloadProgress / 100)" style="transform: rotate(-90deg); transform-origin: center;"/>
              </svg>
              <svg v-else-if="downloadStatus === 'completed'" viewBox="0 0 24 24" fill="none" stroke="#4CAF50">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <svg v-else-if="downloadStatus === 'failed'" viewBox="0 0 24 24" fill="none" stroke="#F44336">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" :stroke="downloadStatus === 'pending' ? '#FF9800' : '#06b6d4'">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              <span v-if="downloadStatus === 'downloading'">{{ downloadProgress }}%</span>
              <span v-else-if="downloadStatus === 'completed'">Downloaded</span>
              <span v-else-if="downloadStatus === 'failed'">Retry Download</span>
              <span v-else-if="downloadStatus === 'pending'">Queued</span>
              <span v-else>Download</span>
            </button>
            <button class="sidebar-action">
              <svg viewBox="0 0 24 24" fill="none" stroke="#8b5cf6">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              Discuss
            </button>
          </div>
        </div>

        <div class="sidebar-section">
          <h3>External Links</h3>
          <div class="link-list">
            <a :href="paper.pdfUrl" target="_blank" class="external-link">
              <svg viewBox="0 0 24 24" fill="none" stroke="#be1234">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              arXiv PDF
            </a>
            <a v-if="paper.codeUrl" :href="paper.codeUrl" target="_blank" class="external-link">
              <svg viewBox="0 0 24 24" fill="none" stroke="#8b5cf6">
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
              </svg>
              GitHub Repository
            </a>
          </div>
        </div>

        <div class="sidebar-section">
          <h3>Discussions</h3>
          <div class="discussion-list">
            <div class="discussion-item">
              <div class="discussion-source">GitHub</div>
              <div class="discussion-title">Issue #42: Questions about implementation</div>
              <div class="discussion-meta">12 comments · 2 days ago</div>
            </div>
            <div class="discussion-item">
              <div class="discussion-source">Twitter</div>
              <div class="discussion-title">Thread: Discussion on methodology</div>
              <div class="discussion-meta">45 replies · 5 days ago</div>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePaperStore } from '../stores/paper-store'
import { useBookmarkStore } from '../stores/bookmark-store'
import { useDownloadStore } from '../stores/download-store'
import { useToastStore } from '../stores/toast-store'
import { getTagStyle, categories } from '../utils/categoryColors'
import { apiService } from '../services/api'
import MarkdownIt from 'markdown-it'
import MarkdownItKatex from 'markdown-it-katex'
import 'katex/dist/katex.min.css'
import type { Paper } from '../types'

const route = useRoute()
const router = useRouter()
const paperStore = usePaperStore()
const bookmarkStore = useBookmarkStore()
const downloadStore = useDownloadStore()
const toastStore = useToastStore()

const loading = ref<boolean>(false)
const error = ref<string | null>(null)
const paper = ref<Paper | null>(null)
const isBookmarked = ref(false)
const downloadStatus = computed(() => {
  if (!paper.value?.id) return 'none'
  const task = downloadStore.tasks.find(t => t.paper_id === paper.value?.id)
  return task?.status || 'none'
})
const downloadProgress = computed(() => {
  if (!paper.value?.id) return 0
  const task = downloadStore.tasks.find(t => t.paper_id === paper.value?.id)
  return task?.progress || 0
})

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
}).use(MarkdownItKatex, {
  throwOnError: false,
  displayMode: false
})

const renderedAbstract = computed(() => {
  if (!paper.value?.abstract) return '<p>No abstract available</p>'
  return md.render(paper.value.abstract)
})

const renderedComment = computed(() => {
  if (!paper.value?.comment) return ''
  return md.render(paper.value.comment)
})

const relatedPapers = computed(() => {
  if (!paper.value) return []
  const currentPaper = paper.value
  return paperStore.papers
    .filter((p: Paper) => p.id !== currentPaper.id && p.category === currentPaper.category)
    .slice(0, 3)
})

const fetchPaperById = async (id: string) => {
  try {
    loading.value = true
    error.value = null
    
    const papers = await paperStore.fetchPapersByIds([id])
    
    if (papers.length === 0) {
      error.value = 'Paper not found'
    } else {
      paper.value = papers[0]
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load paper'
    console.error('Error fetching paper:', err)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const paperId = route.params.id as string
  await fetchPaperById(paperId)
  if (paper.value?.id) {
    isBookmarked.value = await bookmarkStore.checkBookmark(paper.value.id)
    if (downloadStore.tasks.length === 0) {
      await downloadStore.fetchTasks()
    }
  }
})

watch(() => route.params.id, async (newId) => {
  if (newId) {
    await fetchPaperById(newId as string)
    if (paper.value?.id) {
      isBookmarked.value = await bookmarkStore.checkBookmark(paper.value.id)
    }
  }
})

const goToPaper = (id: string) => {
  router.push({ name: 'PaperDetail', params: { id } })
}

const goBack = () => {
  router.back()
}

const toggleBookmark = async () => {
  if (!paper.value?.id) return
  try {
    const result = await bookmarkStore.toggleBookmark({
      paper_id: paper.value.id,
      arxiv_id: paper.value.arxivId,
      title: paper.value.title,
      authors: paper.value.authors,
      abstract: paper.value.abstract,
      comment: paper.value.comment,
      primary_category: paper.value.primaryCategory,
      categories: paper.value.categories,
      pdf_url: paper.value.pdfUrl,
      abs_url: paper.value.absUrl,
      published: paper.value.published?.toString(),
      updated: paper.value.updated?.toString(),
    })
    isBookmarked.value = result
    toastStore.showSuccess(result ? 'Added to bookmarks' : 'Removed from bookmarks')
  } catch (error) {
    console.error('Failed to toggle bookmark:', error)
    toastStore.showError('Failed to update bookmark')
  }
}

const downloadPdf = async () => {
  if (!paper.value?.pdfUrl || !paper.value?.id) return
  
  const existingTask = downloadStore.tasks.find(t => t.paper_id === paper.value?.id)

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
      paper_id: paper.value.id,
      arxiv_id: paper.value.arxivId,
      title: paper.value.title,
      pdf_url: paper.value.pdfUrl,
    })
    toastStore.showSuccess('Download task added to queue')
  } catch (error) {
    console.error('Failed to create download task:', error)
    toastStore.showError('Failed to create download task')
  }
}

const formatDate = (dateStr: string | Date | undefined) => {
  if (!dateStr) return 'Unknown date'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

const getCategoryFullName = (category: string) => {
  if (!category) return 'Unknown Category'
  const categoryData = categories.find(cat => cat.id === category)
  return categoryData?.name || category
}
</script>

<style scoped>
.error-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.error-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 24px;
  color: #ef4444;
}

.error-icon svg {
  width: 100%;
  height: 100%;
}

.error-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.error-state p {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.retry-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  color: white;
  background: var(--accent-color);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-button:hover {
  background: var(--accent-color);
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.loading-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.paper-detail {
  min-height: 100vh;
  padding-top: 64px;
  background: var(--bg-secondary);
}

.detail-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 20px;
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 40px;
}

.main-content {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 32px;
  box-shadow: var(--shadow-md);
}

.paper-header {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: var(--bg-tertiary);
  border-color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.back-button svg {
  width: 20px;
  height: 20px;
}

.header-info {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.paper-id {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 500;
}

.paper-category {
  background: var(--bg-secondary);
  color: var(--text-muted);
  padding: 6px 14px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.paper-date {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.paper-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
  line-height: 1.3;
}

.paper-authors {
  color: var(--text-secondary);
  font-size: 1.1rem;
  margin-bottom: 24px;
  line-height: 1.6;
}

.author {
  color: var(--accent-color);
  cursor: pointer;
  transition: var(--transition);
}

.author:hover {
  text-decoration: underline;
}

.paper-stats {
  display: flex;
  gap: 32px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.stat-item svg {
  width: 20px;
  height: 20px;
}

.paper-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
  text-decoration: none;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
  cursor: pointer;
  background: var(--bg-secondary);
  color: var(--text-muted);
}

.action-button svg {
  width: 20px;
  height: 20px;
}

.action-button.primary {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.action-button.primary:hover {
  background: #764ba2;
  color: white;
  border-color: #764ba2;
  transform: translateY(-2px);
}

.action-button.secondary {
  background: #f093fb;
  color: white;
  border-color: #f093fb;
}

.action-button.secondary:hover {
  background: #f5576c;
  color: white;
  border-color: #f5576c;
  transform: translateY(-2px);
}

.paper-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 32px;
}

.tag {
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 500;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.paper-comments {
  margin-bottom: 40px;
}

.paper-comments h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.comments-content {
  color: var(--text-secondary);
  font-size: 1.05rem;
  line-height: 1.8;
  background: var(--bg-tertiary);
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid var(--accent-color);
}

.comments-content p {
  margin: 0 0 16px 0;
}

.comments-content p:last-child {
  margin-bottom: 0;
}

.comments-content h1,
.comments-content h2,
.comments-content h3 {
  margin: 20px 0 12px 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
}

.comments-content h1 {
  font-size: 1.4rem;
}

.comments-content ul,
.comments-content ol {
  margin: 12px 0 16px 0;
  padding-left: 24px;
}

.comments-content li {
  margin: 6px 0;
  line-height: 1.6;
}

.comments-content code {
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: var(--accent-color);
}

.comments-content pre {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
  border: 1px solid var(--border-color);
}

.comments-content pre code {
  background: transparent;
  padding: 0;
  border-radius: 0;
  color: var(--text-primary);
}

.comments-content strong {
  font-weight: 600;
  color: var(--text-primary);
}

.comments-content em {
  font-style: italic;
}

.comments-content a {
  color: var(--accent-color);
  text-decoration: none;
  transition: color 0.3s ease;
}

.comments-content a:hover {
  text-decoration: underline;
}

.comments-content blockquote {
  border-left: 4px solid var(--accent-color);
  padding-left: 16px;
  margin: 16px 0;
  color: var(--text-secondary);
  font-style: italic;
}

.paper-abstract {
  margin-bottom: 40px;
}

.paper-abstract h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.paper-abstract p {
  color: var(--text-secondary);
  font-size: 1.05rem;
  line-height: 1.8;
}

.abstract-content {
  color: var(--text-secondary);
  font-size: 1.05rem;
  line-height: 1.8;
}

.abstract-content p {
  margin: 0 0 16px 0;
}

.abstract-content p:last-child {
  margin-bottom: 0;
}

.abstract-content h1,
.abstract-content h2,
.abstract-content h3 {
  margin: 20px 0 12px 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
}

.abstract-content h1 {
  font-size: 1.4rem;
}

.abstract-content ul,
.abstract-content ol {
  margin: 12px 0 16px 0;
  padding-left: 24px;
}

.abstract-content li {
  margin: 6px 0;
  line-height: 1.6;
}

.abstract-content code {
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: var(--accent-color);
}

.abstract-content pre {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
  border: 1px solid var(--border-color);
}

.abstract-content pre code {
  background: transparent;
  padding: 0;
  border-radius: 0;
  color: var(--text-primary);
}

.abstract-content strong {
  font-weight: 600;
  color: var(--text-primary);
}

.abstract-content em {
  font-style: italic;
}

.abstract-content a {
  color: var(--accent-color);
  text-decoration: none;
  transition: color 0.3s ease;
}

.abstract-content a:hover {
  text-decoration: underline;
}

.abstract-content blockquote {
  border-left: 4px solid var(--accent-color);
  padding-left: 16px;
  margin: 16px 0;
  color: var(--text-secondary);
  font-style: italic;
}

.ai-insights {
  background: linear-gradient(135deg, rgba(13, 110, 253, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border-color);
}

.ai-insights h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.ai-insights h2 svg {
  width: 24px;
  height: 24px;
  color: var(--accent-color);
}

.insight-card {
  background: var(--bg-primary);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

.insight-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.insight-card ul {
  list-style: none;
  padding: 0;
}

.insight-card li {
  color: var(--text-secondary);
  padding: 8px 0;
  padding-left: 20px;
  position: relative;
}

.insight-card li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--accent-color);
  font-weight: bold;
}

.related-papers {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-paper {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: var(--transition);
}

.related-paper:hover {
  background: var(--bg-tertiary);
  transform: translateX(4px);
}

.related-id {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: var(--text-muted);
  min-width: 80px;
}

.related-title {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.sidebar-section {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
}

.sidebar-section h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-action {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
}

.sidebar-action:hover {
  background: var(--bg-tertiary);
  border-color: var(--accent-color);
  transform: translateX(4px);
}

.sidebar-action.active {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FFD700;
}

.sidebar-action.downloading {
  background: rgba(33, 150, 243, 0.1);
  border-color: #2196F3;
}

.sidebar-action.completed {
  background: rgba(76, 175, 80, 0.1);
  border-color: #4CAF50;
}

.sidebar-action.failed {
  background: rgba(244, 67, 54, 0.1);
  border-color: #F44336;
}

.sidebar-action.pending {
  background: rgba(255, 152, 0, 0.1);
  border-color: #FF9800;
}

.sidebar-action svg {
  width: 18px;
  height: 18px;
}

.link-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.external-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  text-decoration: none;
  transition: var(--transition);
}

.external-link:hover {
  background: var(--bg-tertiary);
  color: var(--accent-color);
}

.external-link svg {
  width: 18px;
  height: 18px;
}

.discussion-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.discussion-item {
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: var(--transition);
}

.discussion-item:hover {
  background: var(--bg-tertiary);
}

.discussion-source {
  display: inline-block;
  padding: 2px 8px;
  background: var(--accent-color);
  color: white;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  margin-bottom: 6px;
}

.discussion-title {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 4px;
}

.discussion-meta {
  color: var(--text-muted);
  font-size: 0.8rem;
}

@media (max-width: 1024px) {
  .detail-container {
    grid-template-columns: 1fr;
  }

  .sidebar {
    order: -1;
  }
}

@media (max-width: 768px) {
  .detail-container {
    padding: 24px 16px;
  }

  .main-content {
    padding: 24px;
  }

  .paper-title {
    font-size: 1.5rem;
  }

  .paper-actions {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
    justify-content: center;
  }

  .paper-stats {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
