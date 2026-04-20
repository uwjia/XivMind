<template>
  <div class="search">
    <div class="search-container">
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Searching...</p>
      </div>

      <template v-else>
        <div v-if="error" class="error-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <h3>Search Error</h3>
          <p>{{ error }}</p>
        </div>

        <template v-else>
          <div class="results-header">
            <div class="results-info">
              <h2 class="results-title">
                {{ totalResults }} {{ totalResults === 1 ? 'paper' : 'papers' }} found
              </h2>
              <span v-if="searchQuery" class="search-query">
                for "<span class="query-text">{{ searchQuery }}</span>"
              </span>
              <span class="search-source-badge" :class="searchSource">
                {{ searchSourceLabel }}
              </span>
            </div>
            <div class="sort-options">
              <select v-model="sortBy" class="sort-select">
                <option value="date">Newest First</option>
                <option value="citations">Most Cited</option>
                <option value="views">Most Viewed</option>
              </select>
            </div>
          </div>

          <div v-if="currentPapers.length > 0" class="papers-list">
            <PaperCard
              v-for="(paper, index) in currentPapers"
              :key="paper.id"
              :paper="paper"
              :index="(currentPage - 1) * pageSize + index + 1"
            />
          </div>

          <div v-if="totalResults > 0 && totalPages > 1" class="pagination">
            <button 
              class="page-btn" 
              :disabled="currentPage === 1" 
              @click="goToPage(currentPage - 1)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <div class="page-numbers">
              <button
                v-for="page in visiblePages"
                :key="page"
                class="page-num"
                :class="{ active: page === currentPage, ellipsis: page === '...' }"
                :disabled="page === '...'"
                @click="page !== '...' && goToPage(page as number)"
              >
                {{ page }}
              </button>
            </div>
            <button 
              class="page-btn" 
              :disabled="currentPage >= totalPages" 
              @click="goToPage(currentPage + 1)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
            <div class="page-jump">
              <span>Go to</span>
              <input 
                type="number" 
                v-model.number="pageInput" 
                :min="1" 
                :max="totalPages"
                @keyup.enter="jumpToPage"
                @blur="jumpToPage"
                class="page-input"
              />
              <span>/ {{ totalPages }}</span>
            </div>
            <span class="page-info">
              {{ totalResults }} items
            </span>
            <div class="page-size-selector">
              <select 
                :value="pageSize" 
                @change="changePageSize(Number(($event.target as HTMLSelectElement).value))"
                class="page-size-select"
              >
                <option v-for="size in pageSizeOptions" :key="size" :value="size">
                  {{ size }} / page
                </option>
              </select>
            </div>
          </div>

          <div v-if="currentPapers.length === 0 && totalResults === 0" class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"/>
              <path d="M21 21l-4.35-4.35"/>
            </svg>
            <h3>No papers found</h3>
            <p>Try adjusting your search terms or filters</p>
          </div>
        </template>
      </template>
    </div>

    <ScrollTopButton />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSearch } from '@/composables/useSearch'
import PaperCard from '@/components/PaperCard.vue'
import ScrollTopButton from '@/components/ScrollTopButton.vue'

const {
  currentPapers,
  isLoading,
  error,
  searchQuery,
  searchSource,
  sortBy,
  totalResults,
  currentPage,
  pageInput,
  pageSize,
  pageSizeOptions,
  totalPages,
  visiblePages,
  goToPage,
  jumpToPage,
  changePageSize
} = useSearch()

const searchSourceLabel = computed(() => {
  switch (searchSource.value) {
    case 'arxiv':
      return 'arXiv API'
    case 'backend':
      return 'Database'
    case 'semantic':
      return 'Semantic'
    default:
      return 'Unknown'
  }
})
</script>

<style scoped>
.search {
  min-height: 100vh;
  padding-top: 64px;
  background: var(--bg-secondary);
}

.search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.error-state svg {
  width: 60px;
  height: 60px;
  margin-bottom: 16px;
  opacity: 0.5;
  color: var(--icon-error);
}

.error-state h3 {
  font-size: 1.5rem;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.error-state p {
  font-size: 1rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.results-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.results-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.search-query {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.query-text {
  color: var(--accent-color);
  font-weight: 500;
}

.search-source-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.search-source-badge.arxiv {
  background: rgba(255, 152, 0, 0.15);
  color: #ff9800;
}

.search-source-badge.backend {
  background: rgba(33, 150, 243, 0.15);
  color: #2196f3;
}

.search-source-badge.semantic {
  background: rgba(156, 39, 176, 0.15);
  color: #9c27b0;
}

.sort-select {
  padding: 8px 32px 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

.papers-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.empty-state svg {
  width: 80px;
  height: 80px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.empty-state p {
  font-size: 1rem;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 32px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 12px;
  flex-wrap: wrap;
}

.page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-secondary);
}

.page-btn:hover:not(:disabled) {
  background: var(--bg-tertiary);
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn svg {
  width: 18px;
  height: 18px;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-num {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  padding: 0 8px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-secondary);
}

.page-num:hover:not(:disabled):not(.ellipsis) {
  background: var(--bg-tertiary);
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.page-num.active {
  background: var(--accent-color);
  border-color: var(--accent-color);
  color: white;
}

.page-num.ellipsis {
  border: none;
  background: transparent;
  cursor: default;
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.page-input {
  width: 60px;
  padding: 6px 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
  text-align: center;
}

.page-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.page-info {
  margin-left: 12px;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.page-size-selector {
  margin-left: 12px;
  padding-left: 12px;
  border-left: 1px solid var(--border-color);
}

.page-size-select {
  padding: 6px 28px 6px 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

.page-size-select:hover {
  border-color: var(--accent-color);
}

.page-size-select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent-color) 20%, transparent);
}

@media (max-width: 768px) {
  .search-container {
    padding: 24px 16px;
  }

  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .results-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .pagination {
    flex-direction: column;
    gap: 12px;
  }

  .page-jump {
    margin-left: 0;
  }

  .page-info {
    margin-left: 0;
  }

  .page-size-selector {
    margin-left: 0;
    padding-left: 0;
    border-left: none;
  }
}
</style>
