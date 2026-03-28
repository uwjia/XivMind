<template>
  <div class="bookmarks-page" :class="{ 'drawer-open': isDrawerOpen }">
    <div class="page-header">
      <div class="header-title">
        <h1>My Bookmarks</h1>
        <span class="total-count" v-if="total > 0">(total {{ total }})</span>
      </div>
      <div class="header-actions">
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
        <button class="drawer-toggle" @click="toggleDrawer" :title="isDrawerOpen ? 'Hide categories' : 'Show categories'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M3 7C3 5.89543 3.89543 5 5 5H9.58579C9.851 5 10.1054 5.10536 10.2929 5.29289L12 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" fill="currentColor" fill-opacity="0.2"/>
          </svg>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading bookmarks...</p>
    </div>

    <div v-else-if="filteredBookmarks.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-empty)">
        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
      </svg>
      <p>{{ selectedCategory ? 'No bookmarks in this category' : 'No bookmarks yet' }}</p>
      <span>{{ selectedCategory ? 'Try selecting a different category' : 'Start bookmarking papers you find interesting!' }}</span>
    </div>

    <div v-else class="bookmarks-list">
      <div v-for="bookmark in filteredBookmarks" :key="bookmark.id" class="bookmark-card">
        <div class="bookmark-header">
          <h3 class="bookmark-title" @click="goToDetail(bookmark.paper_id)">{{ bookmark.title }}</h3>
          <div class="header-badges">
            <span class="primary-category" :style="getCategoryStyle(bookmark.primary_category)">{{ bookmark.primary_category || 'CS' }}</span>
            <button class="remove-btn" @click="removeBookmark(bookmark.paper_id)" title="Remove bookmark">
              <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-bookmarks)">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" fill="var(--icon-bookmarks-active)" stroke="var(--icon-bookmarks-active)"/>
              </svg>
            </button>
          </div>
        </div>
        
        <p class="bookmark-authors">
          <svg class="author-icon" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="7" r="4" fill="var(--icon-author)"/>
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="var(--icon-author)" stroke-width="2"/>
          </svg>
          <span class="author-list">
            <template v-for="(author, idx) in bookmark.authors" :key="idx">
              <span class="author-name" @click.stop="goToAuthorPapers(author)">{{ author }}</span><span v-if="idx < (bookmark.authors?.length || 0) - 1">, </span>
            </template>
            <span v-if="!bookmark.authors?.length">Unknown Authors</span>
          </span>
        </p>
        
        <div class="bookmark-abstract">
          <p>
            <svg class="abstract-icon" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="var(--icon-abstract)" stroke-width="2"/>
              <path d="M2 6h2" stroke="var(--icon-abstract)" stroke-width="2"/>
              <path d="M2 10h2" stroke="var(--icon-abstract)" stroke-width="2"/>
              <path d="M2 14h2" stroke="var(--icon-abstract)" stroke-width="2"/>
              <path d="M2 18h2" stroke="var(--icon-abstract)" stroke-width="2"/>
              <text x="8" y="16" font-size="6" fill="var(--icon-abstract)" font-weight="bold">ABS</text>
            </svg>
            <span v-html="getRenderedAbstract(bookmark.abstract)"></span>
          </p>
        </div>
        
        <div v-if="bookmark.comment" class="bookmark-comments">
          <p>
            <svg class="comments-icon" viewBox="0 0 24 24" fill="none">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="var(--icon-comments)" stroke-width="2"/>
              <path d="M8 6h.01" stroke="var(--icon-comments)" stroke-width="2"/>
              <path d="M12 6h.01" stroke="var(--icon-comments)" stroke-width="2"/>
              <path d="M16 6h.01" stroke="var(--icon-comments)" stroke-width="2"/>
              <text x="8" y="16" font-size="6" fill="var(--icon-comments)" font-weight="bold">COM</text>
            </svg>
            <span v-html="getRenderedComment(bookmark.comment)"></span>
          </p>
        </div>
        
        <div v-if="bookmark.journal_ref" class="bookmark-journal-ref">
          <p>
            <svg class="journal-icon" viewBox="0 0 24 24" fill="none">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" stroke="var(--icon-journal)" stroke-width="2"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" stroke="var(--icon-journal)" stroke-width="2"/>
              <text x="7" y="14" font-size="5" fill="var(--icon-journal)" font-weight="bold">JOU</text>
            </svg>
            <span>{{ bookmark.journal_ref }}</span>
          </p>
        </div>
        
        <div class="bookmark-footer">
          <div class="bookmark-tags">
            <div class="paper-id-section">
              <span class="paper-id">{{ bookmark.paper_id || bookmark.arxiv_id }}</span>
            </div>
            <div class="paper-categories-section">
              <span v-for="cat in (bookmark.categories || []).slice(0, 3)" :key="cat" class="tag" :style="getTagStyle(cat)" :title="getCategoryFullName(cat)">
                {{ getCategoryShortName(cat) }}
              </span>
            </div>
            <div class="paper-published-section">
              <div class="paper-published">Published: {{ formatShortDate(bookmark.published) }}</div>
              <div v-if="bookmark.updated && bookmark.updated !== bookmark.published" class="paper-updated">Updated: {{ formatShortDate(bookmark.updated) }}</div>
            </div>
          </div>
          <div class="bookmark-actions">
            <span v-if="bookmark.doi" class="stat-link" @click="openDoiUrl(bookmark.doi)" title="Open DOI">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-3 3a5 5 0 0 0 .54 7.54z" stroke="var(--icon-doi)" stroke-width="2"/>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l3-3a5 5 0 0 0-.54-7.54z" stroke="var(--icon-doi)" stroke-width="2"/>
                <text x="8" y="15" font-size="5" fill="var(--icon-doi)" font-weight="bold">DOI</text>
              </svg>
            </span>
            <span class="stat-link" @click="openAbsUrl(bookmark.abs_url)" title="Open arXiv page">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-3 3a5 5 0 0 0 .54 7.54z" stroke="var(--icon-link)" stroke-width="2"/>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l3-3a5 5 0 0 0-.54-7.54z" stroke="var(--icon-link)" stroke-width="2"/>
              </svg>
            </span>
            <span class="stat-link" @click="openPdfUrl(bookmark.pdf_url)" title="Open PDF">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="var(--icon-pdf)" stroke-width="2"/>
                <path d="M2 6h2" stroke="var(--icon-pdf)" stroke-width="2"/>
                <path d="M2 10h2" stroke="var(--icon-pdf)" stroke-width="2"/>
                <path d="M2 14h2" stroke="var(--icon-pdf)" stroke-width="2"/>
                <path d="M2 18h2" stroke="var(--icon-pdf)" stroke-width="2"/>
                <text x="8" y="16" font-size="6" fill="var(--icon-pdf)" font-weight="bold">PDF</text>
              </svg>
            </span>
            <span class="stat-link download-btn" :class="getDownloadStatus(bookmark.paper_id)" @click.stop="handleDownloadClick(bookmark)" :title="getDownloadTitle(bookmark.paper_id)">
              <svg v-if="getDownloadStatus(bookmark.paper_id) === 'downloading'" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="var(--icon-downloads)" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="10" stroke="var(--icon-downloads-light)" stroke-width="2" fill="none" stroke-dasharray="62.83" :stroke-dashoffset="62.83 - (62.83 * getDownloadProgress(bookmark.paper_id) / 100)" style="transform: rotate(-90deg); transform-origin: center;"/>
                <text x="12" y="16" font-size="8" fill="var(--icon-downloads)" text-anchor="middle" font-weight="bold">{{ getDownloadProgress(bookmark.paper_id) }}%</text>
              </svg>
              <svg v-else-if="getDownloadStatus(bookmark.paper_id) === 'completed' || isDownloaded(bookmark.paper_id)" viewBox="0 0 24 24" fill="none">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="var(--icon-success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="22 4 12 14.01 9 11.01" stroke="var(--icon-success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="getDownloadStatus(bookmark.paper_id) === 'failed'" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="var(--icon-error)" stroke-width="2"/>
                <line x1="15" y1="9" x2="9" y2="15" stroke="var(--icon-error)" stroke-width="2" stroke-linecap="round"/>
                <line x1="9" y1="9" x2="15" y2="15" stroke="var(--icon-error)" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="var(--icon-downloads)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="7,10 12,15 17,10" stroke="var(--icon-downloads)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="15" x2="12" y2="3" stroke="var(--icon-downloads)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
            <span 
              v-if="getDownloadStatus(bookmark.paper_id) === 'completed' || isDownloaded(bookmark.paper_id)" 
              class="stat-link read-btn" 
              @click.stop="openReader(bookmark.paper_id)" 
              title="Read PDF"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-read)">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" stroke-width="2"/>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" stroke-width="2"/>
              </svg>
            </span>
          </div>
        </div>
        <div class="bookmark-date">
          Bookmarked: {{ formatDateTime(bookmark.created_at) }}
        </div>
      </div>
    </div>

    <div v-if="!loading && filteredBookmarks.length > 0 && totalPages > 1" class="pagination">
      <button class="pagination-btn" @click="goToFirstPage" :disabled="currentPage === 0">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
        </svg>
        First
      </button>
      <button class="pagination-btn" @click="goToPreviousPage" :disabled="currentPage === 0">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        Previous
      </button>
      <div class="pagination-jump">
        <span class="pagination-info">Page {{ currentPage + 1 }} of {{ totalPages }}</span>
        <input 
          type="number" 
          v-model.number="jumpPageInput" 
          class="pagination-input" 
          placeholder="num"
          min="1"
          :max="totalPages"
          @keyup.enter="handleGoToPage"
        />
        <button class="pagination-btn" @click="handleGoToPage">Go</button>
      </div>
      <button class="pagination-btn" @click="goToNextPage" :disabled="currentPage >= totalPages - 1">
        Next
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </button>
    </div>

    <CategoryDrawer
      :is-open="isDrawerOpen"
      :selected-category="selectedCategory"
      :category-counts="categoryCounts"
      @close="closeDrawer"
      @select="handleCategorySelect"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBookmarkActions } from '@/composables/useBookmarkActions'
import { getCategoryFullName, getCategoryShortName } from '@/utils/categoryColors'
import { useDateFormatter } from '@/composables/useDateFormatter'
import CategoryDrawer from '@/components/CategoryDrawer.vue'
import { useDownloadStore } from '@/stores/download-store'

const route = useRoute()
const router = useRouter()
const downloadStore = useDownloadStore()
const { formatShortDate, formatDateTime } = useDateFormatter()
const {
  loading,
  searchQuery,
  isDrawerOpen,
  selectedCategory,
  categoryCounts,
  filteredBookmarks,
  total,
  currentPage,
  totalPages,
  jumpPageInput,
  fetchBookmarks,
  handleSearch,
  removeBookmark,
  goToDetail,
  toggleDrawer,
  closeDrawer,
  handleCategorySelect,
  openAbsUrl,
  openPdfUrl,
  openDoiUrl,
  getRenderedAbstract,
  getRenderedComment,
  getCategoryStyle,
  getTagStyle,
  handleDownloadClick,
  goToFirstPage,
  goToPreviousPage,
  goToNextPage,
  handleGoToPage,
  getDownloadStatus,
  getDownloadProgress,
  getDownloadTitle,
} = useBookmarkActions()

const openReader = (paperId: string) => {
  router.push({ name: 'PdfReader', params: { paperId } })
}

const goToAuthorPapers = (author: string) => {
  router.push({ name: 'AuthorPapers', params: { authorName: encodeURIComponent(author) } })
}

onMounted(() => {
  fetchBookmarks()
})

watch(
  () => route.path,
  (newPath, oldPath) => {
    if (newPath === '/bookmarks') {
      fetchBookmarks()
    }
    if (oldPath === '/bookmarks' && newPath !== '/bookmarks') {
      isDrawerOpen.value = false
    }
  }
)

const isDownloaded = ((id: string) => downloadStore.isDownloaded(id))

watch(filteredBookmarks, async (papers) => {
  if (papers.length > 0) {
    const paperIds = papers.map(p => p.paper_id).filter(Boolean)
    if (paperIds.length > 0) {
      await downloadStore.checkDownloadsBatch(paperIds)
    }
  }
}, { immediate: true })
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
  font-size: 1.75rem;
  font-weight: 600;
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
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid color-mix(in srgb, var(--icon-search) 30%, transparent);
  border-radius: 8px;
  background: color-mix(in srgb, var(--icon-search) 10%, transparent);
  color: var(--icon-search);
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  border-color: color-mix(in srgb, var(--icon-search) 60%, transparent);
  background: color-mix(in srgb, var(--icon-search) 20%, transparent);
  box-shadow: 0 0 20px color-mix(in srgb, var(--icon-search) 30%, transparent), inset 0 0 20px color-mix(in srgb, var(--icon-search) 10%, transparent);
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

.author-list {
  display: inline;
  cursor: default;
}

.author-name {
  display: inline;
  cursor: pointer;
  transition: color 0.2s, text-decoration 0.2s;
}

.author-name:hover {
  color: var(--accent-color);
  text-decoration: underline;
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
  display: inline;
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

.bookmark-journal-ref {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
  margin-bottom: 20px;
}

.bookmark-journal-ref p {
  margin: 0;
}

.bookmark-journal-ref span {
  display: block;
}

.journal-icon {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  margin-right: 8px;
  float: left;
  margin-top: 2px;
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
  color: var(--tag-id);
  background-color: color-mix(in srgb, var(--tag-id) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--tag-id) 30%, transparent);
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
  color: var(--tag-published);
  background-color: color-mix(in srgb, var(--tag-published) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--tag-published) 30%, transparent);
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
  color: var(--tag-updated);
  background-color: color-mix(in srgb, var(--tag-updated) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--tag-updated) 30%, transparent);
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
  color: var(--icon-success);
}

.download-btn.failed svg {
  color: var(--icon-error);
}

.download-btn.pending svg {
  color: var(--icon-comments);
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.drawer-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid color-mix(in srgb, var(--icon-filter) 30%, transparent);
  border-radius: 8px;
  background: color-mix(in srgb, var(--icon-filter) 10%, transparent);
  cursor: pointer;
  transition: all 0.3s ease;
}

.drawer-toggle:hover {
  border-color: color-mix(in srgb, var(--icon-filter) 60%, transparent);
  background: color-mix(in srgb, var(--icon-filter) 20%, transparent);
  box-shadow: 0 0 20px color-mix(in srgb, var(--icon-filter) 30%, transparent), inset 0 0 20px color-mix(in srgb, var(--icon-filter) 10%, transparent);
}

.drawer-toggle svg {
  width: 20px;
  height: 20px;
  color: var(--icon-filter);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h1 {
  margin: 0;
}

.total-count {
  font-size: 1rem;
  color: var(--text-secondary);
  font-weight: 400;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 32px;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.pagination-btn {
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
  border: 1px solid #667eea;
  cursor: pointer;
  background: #667eea;
  color: white;
}

.pagination-btn svg {
  width: 20px;
  height: 20px;
}

.pagination-btn:hover:not(:disabled) {
  background: #764ba2;
  color: white;
  border-color: #764ba2;
  transform: translateY(-2px);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.pagination-jump {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-info {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
  min-width: 80px;
  text-align: center;
  padding: 6px 14px;
}

.pagination-input {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  width: 60px;
  text-align: center;
}

.pagination-input:focus {
  outline: none;
  border-color: #667eea;
}
</style>
